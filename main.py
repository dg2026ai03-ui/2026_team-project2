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
# 추가 변수 (1,2,4번 기능)
# ================================
peak_ppm      = 0        # 1️⃣ 최고치 기록
warn_count    = 0        # 2️⃣ 경고 횟수
start_time    = time.ticks_ms()  # 4️⃣ 측정 시작 시간
history       = []       # 공기질 예보용

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
# 안전 : 파도 그라데이션
# ================================
def safe_mode(ppm):
    steps = 60
    for step in range(steps):
        for i in range(NUM_LEDS):
            wave = math.sin((step / steps * math.pi * 2) + (i / NUM_LEDS * math.pi * 2))
            wave = (wave + 1) / 2
            g_val = int(wave * 180)
            b_val = int(255 - wave * 150)
            led[i] = (0, g_val, b_val)
        led.write()
        time.sleep(0.03)

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
# 위험 : 빨강 번쩍
# ================================
def danger_mode(ppm):
    for _ in range(6):
        set_color(255, 0, 0)
        time.sleep(0.04)
        set_gauge(ppm)
        time.sleep(0.04)

# ================================
# 1️⃣ 최고치 기록 함수
# ================================
def update_peak(ppm):
    global peak_ppm
    if ppm > peak_ppm:
        peak_ppm = ppm
        print(f"  🏆 최고치 갱신! → {peak_ppm:.1f} PPM")

# ================================
# 2️⃣ 경고 횟수 카운터
# ================================
def update_warn_count(ppm, prev_status):
    global warn_count
    if ppm >= WARN_THRESHOLD and prev_status == "안전 🟢":
        warn_count += 1
        print(f"  ⚠️  경고 발생! 누적 횟수 : {warn_count}회")

# ================================
# 4️⃣ 측정 시간 계산
# ================================
def get_elapsed_time():
    elapsed = time.ticks_diff(time.ticks_ms(), start_time) // 1000
    minutes = elapsed // 60
    seconds = elapsed % 60
    return f"{minutes}분 {seconds}초"

# ================================
# 공기질 예보
# ================================
def get_forecast(ppm):
    global history
    history.append(ppm)
    if len(history) > 3:
        history.pop(0)
    if len(history) < 3:
        return f"➡️ 측정 중... ({len(history)}/3)"
    diff = history[2] - history[0]
    if diff > 2:
        return "📈 공기질 나빠지는 중!"
    elif diff < -2:
        return "📉 공기질 좋아지는 중!"
    else:
        return "➡️ 공기질 유지 중!"

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

prev_status = "안전 🟢"   # 이전 상태 저장 (2번 기능용)

while True:
    raw_value = mq2.read_u16()
    ppm       = convert_to_ppm(raw_value)
    status    = get_status(ppm)
    forecast  = get_forecast(ppm)

    # 1️⃣ 최고치 업데이트
    update_peak(ppm)

    # 2️⃣ 경고 횟수 업데이트
    update_warn_count(ppm, prev_status)

    # ================================
    # 시리얼 출력
    # ================================
    print("=" * 40)
    print(f"  🕐 측정 시간  : {get_elapsed_time()}")       # 4️⃣
    print(f"  📊 현재 PPM   : {ppm:.1f}")
    print(f"  🏆 최고 PPM   : {peak_ppm:.1f}")             # 1️⃣
    print(f"  ⚠️  경고 횟수  : {warn_count}회")             # 2️⃣
    print(f"  📍 현재 상태  : {status}")
    print(f"  {forecast}")
    print("=" * 40)

    # LED 효과
    if ppm < SAFE_THRESHOLD:
        safe_mode(ppm)

    elif ppm < WARN_THRESHOLD:
        warning_mode(ppm)

    else:
        danger_mode(ppm)

    prev_status = status   # 이전 상태 저장
