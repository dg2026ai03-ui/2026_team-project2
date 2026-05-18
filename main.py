from machine import Pin, ADC
from neopixel import NeoPixel
import time

# ================================
# 핀 설정
# ================================
mq2 = ADC(26)  # MQ2 → A0 (GP26)

# 네오픽셀 LED 설정
TIMING = (280, 515, 515, 745)
led = NeoPixel(Pin(16), 1, timing=TIMING)

# ================================
# 임계값 설정
# ================================
SAFE_THRESHOLD = 20000
WARN_THRESHOLD = 40000

# ================================
# 네오픽셀 색상 함수
# ================================
def set_color(r, g, b):
    led[0] = (r, g, b)
    led.write()

def led_off():
    set_color(0, 0, 0)

# ================================
# 안전 : 초록↔파랑 파도처럼 일렁
# ================================
def safe_mode():
    import math
    steps = 40
    for i in range(steps):
        wave  = math.sin(i / steps * math.pi * 2)
        g_val = int(200 + wave * 55)
        b_val = int(200 - wave * 55)
        set_color(0, g_val, b_val)
        time.sleep(0.03)

# ================================
# 주의 : 노랑 천천히 깜빡
# ================================
def warning_mode():
    steps = 30
    for i in range(steps):
        brightness = int((i / steps) * 255)
        set_color(brightness, brightness, 0)
        time.sleep(0.02)
    for i in range(steps, 0, -1):
        brightness = int((i / steps) * 255)
        set_color(brightness, brightness, 0)
        time.sleep(0.02)

# ================================
# 위험 : 빨강 엄청 빠르게 번쩍
# ================================
def danger_mode():
    for _ in range(6):
        set_color(255, 0, 0)
        time.sleep(0.04)
        led_off()
        time.sleep(0.04)

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
# 시리얼 막대그래프
# ================================
def print_bar(raw_value, status):
    ppm   = (raw_value / 65535) * 1000
    count = int((raw_value / 65535) * 10)
    count = max(0, min(10, count))
    bar   = "█" * count + "░" * (10 - count)
    print(f"[{bar}] {status} | PPM:{ppm:.1f} | RAW:{raw_value}")

# ================================
# 워밍업
# ================================
def warmup():
    print("=" * 40)
    print("  가스누출 경보 위험도 시각화 시스템")
    print("  MQ-2 워밍업 중... (20초)")
    print("=" * 40)
    for i in range(20, 0, -1):
        set_color(255, 255, 255)
        time.sleep(0.3)
        led_off()
        time.sleep(0.3)
        print(f"  워밍업 남은 시간 : {i}초")
    led_off()
    print("  ✅ 준비 완료! 모니터링 시작!")
    print("=" * 40)

# ================================
# 메인 루프
# ================================
warmup()

while True:
    raw_value = mq2.read_u16()
    status    = get_status(raw_value)

    print_bar(raw_value, status)

    if raw_value < SAFE_THRESHOLD:
        safe_mode()       # 🟢 초록↔파랑 파도처럼 일렁

    elif raw_value < WARN_THRESHOLD:
        warning_mode()    # 🟡 노랑 천천히 깜빡깜빡

    else:
        danger_mode()     # 🔴 빨강 엄청 빠르게 번쩍번쩍
