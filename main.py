from machine import Pin, ADC
import time

# ================================
# 핀 설정
# ================================
mq2 = ADC(26)          # MQ2 → A0 (GP26)
led = Pin(27, Pin.OUT) # LED → A1 (GP27)

# ================================
# 임계값 설정
# ================================
SAFE_THRESHOLD = 20000
WARN_THRESHOLD = 40000

# ================================
# 안전 : 천천히 깜빡
# ================================
def safe_mode():
    led.on()
    time.sleep(0.8)
    led.off()
    time.sleep(0.8)

# ================================
# 주의 : 보통 속도 깜빡
# ================================
def warning_mode():
    led.on()
    time.sleep(0.3)
    led.off()
    time.sleep(0.3)

# ================================
# 위험 : 엄청 빠르게 번쩍
# ================================
def danger_mode():
    led.on()
    time.sleep(0.05)
    led.off()
    time.sleep(0.05)

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
# 메인 루프
# ================================
print("=" * 40)
print("  가스누출 경보 시스템 시작!")
print("=" * 40)

while True:
    raw_value = mq2.read_u16()
    status    = get_status(raw_value)
    ppm       = (raw_value / 65535) * 1000

    print(f"RAW:{raw_value} | PPM:{ppm:.1f} | {status}")

    if raw_value < SAFE_THRESHOLD:
        safe_mode()       # 🟢 천천히 깜빡

    elif raw_value < WARN_THRESHOLD:
        warning_mode()    # 🟡 보통 속도 깜빡

    else:
        danger_mode()     # 🔴 엄청 빠르게 번쩍번쩍
