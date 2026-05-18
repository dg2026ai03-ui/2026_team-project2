from machine import Pin, ADC, PWM
import time

# ================================
# 핀 설정
# ================================
mq2 = ADC(26)

red   = PWM(Pin(13))
green = PWM(Pin(14))
blue  = PWM(Pin(15))

red.freq(1000)
green.freq(1000)
blue.freq(1000)

# ================================
# 임계값 설정
# ================================
SAFE_THRESHOLD = 20000
WARN_THRESHOLD = 40000

# ================================
# RGB LED 색상 함수
# ================================
def set_color(r, g, b):
    red.duty_u16(int(r * 257))
    green.duty_u16(int(g * 257))
    blue.duty_u16(int(b * 257))

# ================================
# 안전 : 초록↔파랑 파도처럼 일렁
# ================================
def safe_mode():
    import math
    # 한 사이클 동안 파도 효과
    steps = 40
    for i in range(steps):
        # sin 파형으로 부드럽게 일렁
        wave = math.sin(i / steps * math.pi * 2)
        
        # 초록 : 150~255 사이에서 출렁
        g_val = int(200 + wave * 55)
        # 파랑 : 초록과 반대로 출렁
        b_val = int(200 - wave * 55)
        # 빨강은 살짝만
        r_val = 0
        
        set_color(r_val, g_val, b_val)
        time.sleep(0.03)   # 전체 약 1.2초 한 사이클

# ================================
# 주의 : 노랑 천천히 깜빡
# ================================
def warning_mode():
    # 서서히 밝아졌다 어두워지기
    steps = 30
    # 밝아지기
    for i in range(steps):
        brightness = int((i / steps) * 255)
        set_color(brightness, brightness, 0)
        time.sleep(0.02)
    # 어두워지기
    for i in range(steps, 0, -1):
        brightness = int((i / steps) * 255)
        set_color(brightness, brightness, 0)
        time.sleep(0.02)

# ================================
# 위험 : 빨강 매우 빠르게 깜빡
# ================================
def danger_mode():
    # 빠른 점멸 5회
    for _ in range(5):
        set_color(255, 0, 0)
        time.sleep(0.05)
        set_color(0, 0, 0)
        time.sleep(0.05)

# ================================
# ppm 변환
# ================================
def convert_to_ppm(raw_value):
    ppm = (raw_value / 65535) * 1000
    return ppm

# ================================
# 상태 확인
# ================================
def get_status(raw_value):
    if raw_value < SAFE_THRESHOLD:
        return "안전"
    elif raw_value < WARN_THRESHOLD:
        return "주의"
    else:
        return "위험"

# ================================
# 메인 루프
# ================================
print("=" * 40)
print("  가스 모니터링 시작!")
print("=" * 40)

while True:
    raw_value = mq2.read_u16()
    ppm       = convert_to_ppm(raw_value)
    status    = get_status(raw_value)

    print(f"RAW: {raw_value} | PPM: {ppm:.1f} | 상태: {status}")

    if raw_value < SAFE_THRESHOLD:
        safe_mode()       # 🟢 초록↔파랑 잔잔하게 일렁

    elif raw_value < WARN_THRESHOLD:
        warning_mode()    # 🟡 노랑 천천히 깜빡

    else:
        danger_mode()     # 🔴 빨강 엄청 빠르게 깜빡
