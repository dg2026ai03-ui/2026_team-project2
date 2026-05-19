from machine import Pin, ADC
from neopixel import NeoPixel
import time
import math

# ================================
# 핀 설정
# ================================
mq2 = ADC(26)
TIMING = (280, 515, 515, 745)
NUM_LEDS = 10  # ✅ 10개!
led = NeoPixel(Pin(16), NUM_LEDS, timing=TIMING)  # ✅ 10개로 변경!

# ================================
# 임계값 설정
# ================================
SAFE_THRESHOLD = 120
WARN_THRESHOLD = 150

# ================================
# 네오픽셀 색상 함수 ✅ 10개 전부!
# ================================
def set_color(r, g, b):
    for i in range(NUM_LEDS):  # ✅ 10개 전부 같은 색!
        led[i] = (r, g, b)
    led.write()

def led_off():
    set_color(0, 0, 0)

# ================================
# 안전 : 초록↔파랑 파도처럼 일렁
# ================================
def safe_mode():
    steps = 40
    for i in range(steps):
        wave  = math.sin(i / steps * math.pi * 2)
        g_val = int(127 + wave * 127)
        b_val = int(127 - wave * 127)
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
        set_color(50, 50, 50)  # ✅ 흰색 약하게
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
        safe_mode()       # 🟢 초록↔파랑

    elif ppm < WARN_THRESHOLD:
        warning_mode()    # 🟡 노랑 깜빡

    else:
        danger_mode()     # 🔴 빨강 번쩍
