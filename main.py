# Level 2 : 통계 기능 추가
from machine import Pin, ADC, PWM
import time
import math

mq2 = ADC(26)
red   = PWM(Pin(13))
green = PWM(Pin(14))
blue  = PWM(Pin(15))

red.freq(1000)
green.freq(1000)
blue.freq(1000)

SAFE_THRESHOLD = 20000
WARN_THRESHOLD = 40000

# ================================
# 통계 변수 추가
# ================================
count = 0
max_ppm = 0
min_ppm = 9999
total_ppm = 0
warn_count = 0
danger_count = 0

def set_color(r, g, b):
    red.duty_u16(int(r * 257))
    green.duty_u16(int(g * 257))
    blue.duty_u16(int(b * 257))

def safe_mode():
    steps = 40
    for i in range(steps):
        wave = math.sin(i / steps * math.pi * 2)
        g_val = int(200 + wave * 55)
        b_val = int(200 - wave * 55)
        set_color(0, g_val, b_val)
        time.sleep(0.03)

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

def danger_mode():
    for _ in range(5):
        set_color(255, 0, 0)
        time.sleep(0.05)
        set_color(0, 0, 0)
        time.sleep(0.05)

def convert_to_ppm(raw_value):
    return (raw_value / 65535) * 1000

def get_status(raw_value):
    if raw_value < SAFE_THRESHOLD:
        return "안전"
    elif raw_value < WARN_THRESHOLD:
        return "주의"
    else:
        return "위험"

# ================================
# 통계 출력 함수 추가
# ================================
def print_stats():
    avg_ppm = total_ppm / count if count > 0 else 0
    print("-" * 40)
    print(f"  📊 통계 리포트 (측정 {count}회)")
    print(f"  최대 농도: {max_ppm:.1f} ppm")
    print(f"  최소 농도: {min_ppm:.1f} ppm")
    print(f"  평균 농도: {avg_ppm:.1f} ppm")
    print(f"  주의 발생: {warn_count}회")
    print(f"  위험 발생: {danger_count}회")
    print("-" * 40)

print("=" * 40)
print("  가스 모니터링 시작! (Level 2)")
print("=" * 40)

while True:
    raw_value = mq2.read_u16()
    ppm = convert_to_ppm(raw_value)
    status = get_status(raw_value)

    # 통계 업데이트
    count += 1
    total_ppm += ppm
    if ppm > max_ppm:
        max_ppm = ppm
    if ppm < min_ppm:
        min_ppm = ppm
    if status == "주의":
        warn_count += 1
    elif status == "위험":
        danger_count += 1

    print(f"[{count}회] RAW: {raw_value} | PPM: {ppm:.1f} | 상태: {status}")

    # 10회마다 통계 출력
    if count % 10 == 0:
        print_stats()

    if raw_value < SAFE_THRESHOLD:
        safe_mode()
    elif raw_value < WARN_THRESHOLD:
        warning_mode()
    else:
        danger_mode()

    time.sleep(1)
