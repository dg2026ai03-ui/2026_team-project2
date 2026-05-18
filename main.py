# Level 1 : 기본 가스 모니터링
# 추가 기능 없음 / LED 효과만

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

print("=" * 40)
print("  가스 모니터링 시작! (Level 1)")
print("=" * 40)

while True:
    raw_value = mq2.read_u16()
    ppm = convert_to_ppm(raw_value)
    status = get_status(raw_value)

    print(f"RAW: {raw_value} | PPM: {ppm:.1f} | 상태: {status}")

    if raw_value < SAFE_THRESHOLD:
        safe_mode()
    elif raw_value < WARN_THRESHOLD:
        warning_mode()
    else:
        danger_mode()

    time.sleep(1)
