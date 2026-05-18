from machine import Pin, ADC
import time

# ================================
# 핀 설정
# ================================
mq2 = ADC(26)  # MQ2 → A0 (GP26)

# LED 10개 (GP0 ~ GP9)
leds = [Pin(i, Pin.OUT) for i in range(10)]

# ================================
# 임계값 설정
# ================================
SAFE_THRESHOLD = 20000
WARN_THRESHOLD = 40000

# ================================
# LED 제어 함수
# ================================
def all_off():
    for led in leds:
        led.off()

def set_leds(count):
    all_off()
    for i in range(count):
        leds[i].on()

# ================================
# 안전 : 파도처럼 출렁
# ================================
def safe_mode(count):
    for i in range(count):
        all_off()
        leds[i].on()
        time.sleep(0.08)
    for i in range(count - 1, -1, -1):
        all_off()
        leds[i].on()
        time.sleep(0.08)

# ================================
# 주의 : 천천히 깜빡
# ================================
def warning_mode(count):
    set_leds(count)
    time.sleep(0.5)
    all_off()
    time.sleep(0.5)

# ================================
# 위험 : 전체 엄청 빠르게 번쩍
# ================================
def danger_mode():
    for _ in range(6):
        for led in leds:
            led.on()
        time.sleep(0.04)
        all_off()
        time.sleep(0.04)

# ================================
# 센서값 → LED 개수 변환
# ================================
def get_count(raw_value):
    count = int((raw_value / 65535) * 10)
    return max(1, min(10, count))

# ================================
# ppm 변환
# ================================
def get_ppm(raw_value):
    return (raw_value / 65535) * 1000

# ================================
# 상태 확인
# ================================
def get_status(raw_value):
    if raw_value < SAFE_THRESHOLD:
        return "안전 🟢"
    elif raw_value < WARN_THRESHOLD:
        return "주의 🟡"
    else:
        return "위험 🔴"

# ================================
# 시리얼 막대그래프 출력
# ================================
def print_bar(raw_value, count, status):
    bar = "█" * count + "░" * (10 - count)
    ppm = get_ppm(raw_value)
    print(f"[{bar}] {count}/10 | {status} | PPM:{ppm:.1f} | RAW:{raw_value}")

# ================================
# 워밍업
# ================================
def warmup():
    print("=" * 45)
    print("  가스누출 경보 위험도 시각화 시스템")
    print("  MQ-2 워밍업 중... (20초)")
    print("=" * 45)
    for i in range(20, 0, -1):
        for led in leds:
            led.on()
        time.sleep(0.3)
        all_off()
        time.sleep(0.3)
        print(f"  워밍업 남은 시간 : {i}초")
    all_off()
    print("  ✅ 준비 완료! 모니터링 시작!")
    print("=" * 45)

# ================================
# 메인 루프
# ================================
warmup()

while True:
    raw_value = mq2.read_u16()
    count     = get_count(raw_value)
    status    = get_status(raw_value)

    print_bar(raw_value, count, status)

    if raw_value < SAFE_THRESHOLD:
        safe_mode(count)        # 🟢 파도처럼 출렁출렁

    elif raw_value < WARN_THRESHOLD:
        warning_mode(count)     # 🟡 천천히 깜빡깜빡

    else:
        danger_mode()           # 🔴 전체 엄청 빠르게 번쩍번쩍
