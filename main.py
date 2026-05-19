from machine import Pin, ADC
from neopixel import NeoPixel
import time
import math

# ================================
# 핀 설정
# ================================
mq2 = ADC(26)
TIMING = (280, 515, 515, 745)
NUM_LEDS = 10
led = NeoPixel(Pin(16), NUM_LEDS, timing=TIMING)

# ================================
# 임계값 설정
# ================================
SAFE_THRESHOLD = 120
WARN_THRESHOLD = 150

# ================================
# 네오픽셀 색상 함수
# ================================
def set_color(r, g, b):
    for i in range(NUM_LEDS):
        led[i] = (r, g, b)
    led.write()

def led_off():
    set_color(0, 0, 0)

# ================================
# 안전 : 자연스러운 그라데이션 🌊
# ================================
def safe_mode():
    steps = 100  # ✅ 더 촘촘하게!
    for i in range(steps):
        t = i / steps

        # ✅ 사인파로 부드럽게 전환!
        wave = (math.sin(t * math.pi * 2 - math.pi / 2) + 1) / 2

        # 청록색(0,200,200) → 파랑(0,50,255) → 청록색 반복
        r_val = 0
        g_val = int(200 - wave * 150)  # 200 → 50 → 200
        b_val = int(200 + wave * 55)   # 200 → 255 → 200

        set_color(r_val, g_val, b_val)
        time.sleep(0.02)

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
# PPM 변환
# ================================
def convert_to_ppm(raw_value):
    return (raw_value / 65535) * 1000

# ================================
# 상태 확인
# ================================
def get_status(ppm):
    if ppm < SAFE_THRESHOLD:
        return "안전 🟢"
    elif ppm < WARN_THRESHOLD:
        return "주의 🟡"
    else:
        return "위험 🔴"

# ================================
# 시리얼 막대그래프
# ================================
def print_bar(ppm, status):
    count = int((ppm / 200) * 10)
    count = max(0, min(10, count))
    bar   = "█" * count + "░" * (10 - count)
    print(f"[{bar}] {status} | PPM:{ppm:.1f}")

# ================================
# 워밍업
# ================================
def warmup():
    print("=" * 40)
    print("  가스누출 경보 위험도 시각화 시스템")
    print("  MQ-2 워밍업 중... (20초)")
    print("=" * 40)
    for i in range(20, 0, -1):
        set_color(50, 50, 50)
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
    ppm       = convert_to_ppm(raw_value)
    status    = get_status(ppm)

    print_bar(ppm, status)

    if ppm < SAFE_THRESHOLD:
        safe_mode()       # 🟢 청록↔파랑 그라데이션

    elif ppm < WARN_THRESHOLD:
        warning_mode()    # 🟡 노랑 깜빡

    else:
        danger_mode()     # 🔴 빨강 번쩍
