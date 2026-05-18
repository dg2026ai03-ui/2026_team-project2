from machine import Pin, ADC, PWM
import time

# ================================
# 핀 설정
# ================================
mq2 = ADC(26)           # MQ2 센서 → GP26

# RGB LED PWM 설정
red = PWM(Pin(13))
green = PWM(Pin(14))
blue = PWM(Pin(15))

# PWM 주파수 설정
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
    # 0~255 값을 0~65535로 변환
    red.duty_u16(int(r * 257))
    green.duty_u16(int(g * 257))
    blue.duty_u16(int(b * 257))

def safe_mode():
    # 초록색
    set_color(0, 255, 0)

def warning_mode():
    # 노랑색
    set_color(255, 255, 0)

def danger_mode():
    # 빨강 점멸
    set_color(255, 0, 0)
    time.sleep(0.2)
    set_color(0, 0, 0)
    time.sleep(0.2)

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
