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
# 공기질 예보 변수
# ================================
prev_ppm = None   # 직전 측정값 저장

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
# LED 게이지 함수
# ================================
def set_gauge(ppm):
    count = int((ppm / 200) * NUM_LEDS)
    count = max(0, min(NUM_LEDS, count))

    for i in range(NUM_LEDS):
        if i < count:
            if ppm < SAFE_THRESHOLD:
                led[i] = (0, 255, 0)
            elif ppm < WARN_THRESHOLD:
                led[i] = (255, 255, 0)
            else:
                led[i] = (255, 0, 0)
        else:
            led[i] = (0, 0, 0)
    led.write()

# ================================
# 안전 : 청록↔파랑 그라데이션
# ================================
def safe_mode(ppm):
    steps = 40
    for i in range(steps):
        t = i / steps
        wave = (math.sin(t * math.pi * 2 - math.pi / 2) + 1) / 2
        g_val = int(200 - wave * 150)
        b_val = int(200 + wave * 55)
        set_color(0, g_val, b_val)
        time.sleep(0.02)
    set_gauge(ppm)

# ================================
# 주의 : 노랑 천천히 깜빡
# ================================
def warning_mode(ppm):
    steps = 30
    for i in range(steps):
        brightness = int((i / steps) * 255)
        set_color(brightness, brightness, 0)
        time.sleep(0.02)
    for i in range(steps, 0, -1):
        brightness = int((i / steps) * 255)
        set_color(brightness, brightness, 0)
        time.sleep(0.02)
    set_gauge(ppm)

# ================================
# 위험 : 빨강 번쩍 + 게이지
# ================================
def danger_mode(ppm):
    for _ in range(6):
        set_color(255, 0, 0)
        time.sleep(0.04)
        set_gauge(ppm)
        time.sleep(0.04)

# ================================
# 📈 공기질 예보 함수
# ================================
def get_forecast(ppm):
    global prev_ppm

    # 첫 측정은 비교 불가
    if prev_ppm is None:
        prev_ppm = ppm
        return "➡️ 측정 중..."

    # 직전 값과 비교
    diff = ppm - prev_ppm

    if diff > 2:        # 2 이상 올라가면
        forecast = "📈 공기질 나빠지는 중!"
    elif diff < -2:     # 2 이상 내려가면
        forecast = "📉 공기질 좋아지는 중!"
    else:               # 2 이내면 유지
        forecast = "➡️ 공기질 유지 중!"

    # 현재값을 이전값으로 저장
    prev_ppm = ppm

    return forecast

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
    forecast  = get_forecast(ppm)   # 📈 예보 계산

    # PPM + 기준선 + 예보 출력!
    print(ppm, SAFE_THRESHOLD, WARN_THRESHOLD)
    print(f"  {forecast}")

    if ppm < SAFE_THRESHOLD:
        safe_mode(ppm)

    elif ppm < WARN_THRESHOLD:
        warning_mode(ppm)

    else:
        danger_mode(ppm)
