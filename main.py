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
# 임계값 설정 (수정완료!)
# ================================
SAFE_THRESHOLD = 210    # 120 → 210
WARN_THRESHOLD = 230    # 150 → 230

# ================================
# 추가 변수
# ================================
peak_ppm   = 0
warn_count = 0
start_time = time.ticks_ms()
history    = []

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
# 1️⃣ 최고치 기록
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
# 4️⃣ 측정 시간
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

prev_status = "안전 🟢"

while True:
    raw_value = mq2.read_u16()
    ppm       = convert_to_ppm(raw_value)
    status    = get_status(ppm)
    forecast  = get_forecast(ppm)

    update_peak(ppm)
    update_warn_count(ppm, prev_status)

    print("=" * 40)
    print(f"  🕐 측정 시간  : {get_elapsed_time()}")
    print(f"  📊 현재 PPM   : {ppm:.1f}")
    print(f"  🏆 최고 PPM   : {peak_ppm:.1f}")
    print(f"  ⚠️  경고 횟수  : {warn_count}회")
    print(f"  📍 현재 상태  : {status}")
    print(f"  {forecast}")
    print("=" * 40)

    if ppm < SAFE_THRESHOLD:
        safe_mode(ppm)
    elif ppm < WARN_THRESHOLD:
        warning_mode(ppm)
    else:
        danger_mode(ppm)

    prev_status = status




 #웹앱사이트









import network
import socket
import time
import math
from machine import Pin, ADC
from neopixel import NeoPixel
import json

# ================================
# 와이파이 설정 (여기만 바꾸세요!)
# ================================
WIFI_SSID     = "여기에 와이파이이름"
WIFI_PASSWORD = "여기에 비밀번호"

# ================================
# 핀 설정
# ================================
mq2    = ADC(26)
TIMING = (280, 515, 515, 745)
NUM_LEDS = 10
led    = NeoPixel(Pin(16), NUM_LEDS, timing=TIMING)

# ================================
# 임계값
# ================================
SAFE_THRESHOLD = 210
WARN_THRESHOLD = 230

# ================================
# 전역 변수
# ================================
peak_ppm   = 0
warn_count = 0
start_time = time.ticks_ms()
history    = []
ppm_log    = []   # 그래프용 로그 (최근 20개)

# ================================
# 네오픽셀
# ================================
def set_color(r, g, b):
    for i in range(NUM_LEDS):
        led[i] = (r, g, b)
    led.write()

def led_off():
    set_color(0, 0, 0)

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

def safe_mode(ppm):
    steps = 30
    for step in range(steps):
        for i in range(NUM_LEDS):
            wave  = math.sin((step / steps * math.pi * 2) + (i / NUM_LEDS * math.pi * 2))
            wave  = (wave + 1) / 2
            g_val = int(wave * 180)
            b_val = int(255 - wave * 150)
            led[i] = (0, g_val, b_val)
        led.write()
        time.sleep(0.03)

def warning_mode(ppm):
    steps = 20
    for i in range(steps):
        brightness = int((i / steps) * 255)
        set_color(brightness, brightness, 0)
        time.sleep(0.02)
    for i in range(steps, 0, -1):
        brightness = int((i / steps) * 255)
        set_color(brightness, brightness, 0)
        time.sleep(0.02)
    set_gauge(ppm)

def danger_mode(ppm):
    for _ in range(6):
        set_color(255, 0, 0)
        time.sleep(0.04)
        set_gauge(ppm)
        time.sleep(0.04)

# ================================
# 데이터 함수
# ================================
def update_peak(ppm):
    global peak_ppm
    if ppm > peak_ppm:
        peak_ppm = ppm

def update_warn_count(ppm, prev_status):
    global warn_count
    if ppm >= WARN_THRESHOLD and prev_status == "안전":
        warn_count += 1

def get_elapsed_time():
    elapsed = time.ticks_diff(time.ticks_ms(), start_time) // 1000
    minutes = elapsed // 60
    seconds = elapsed % 60
    return f"{minutes}분 {seconds}초"

def get_forecast(ppm):
    global history
    history.append(ppm)
    if len(history) > 3:
        history.pop(0)
    if len(history) < 3:
        return "측정 중..."
    diff = history[2] - history[0]
    if diff > 2:
        return "📈 나빠지는 중"
    elif diff < -2:
        return "📉 좋아지는 중"
    else:
        return "➡️ 유지 중"

def convert_to_ppm(raw_value):
    return (raw_value / 65535) * 1000

def get_status(ppm):
    if ppm < SAFE_THRESHOLD:
        return "안전"
    elif ppm < WARN_THRESHOLD:
        return "주의"
    else:
        return "위험"

def update_log(ppm):
    global ppm_log
    ppm_log.append(round(ppm, 1))
    if len(ppm_log) > 20:
        ppm_log.pop(0)

# ================================
# 와이파이 연결
# ================================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("와이파이 연결 중...")
    for i in range(20):
        if wlan.isconnected():
            print(f"✅ 연결 성공! IP: {wlan.ifconfig()[0]}")
            return wlan.ifconfig()[0]
        time.sleep(1)
        print(f"  연결 시도 중... {i+1}/20")
    print("❌ 연결 실패!")
    return None

# ================================
# 웹 페이지 HTML
# ================================
def get_html(ppm, status, peak, warns, elapsed, forecast, log):
    if status == "안전":
        color     = "#00ff88"
        bg_color  = "#003322"
        status_kr = "안전 🟢"
    elif status == "주의":
        color     = "#ffff00"
        bg_color  = "#333300"
        status_kr = "주의 🟡"
    else:
        color     = "#ff3333"
        bg_color  = "#330000"
        status_kr = "위험 🔴"

    log_str = str(log).replace("'", '"')

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="3">
    <title>가스 모니터링</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            background: #111;
            color: white;
            font-family: 'Arial', sans-serif;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
            font-size: 1.4em;
            margin-bottom: 20px;
            color: #aaa;
        }}
        .card {{
            background: #1e1e1e;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            border: 1px solid #333;
        }}
        .status-card {{
            background: {bg_color};
            border: 2px solid {color};
            text-align: center;
        }}
        .status-text {{
            font-size: 2.5em;
            font-weight: bold;
            color: {color};
        }}
        .ppm-big {{
            font-size: 3.5em;
            font-weight: bold;
            color: {color};
            text-align: center;
        }}
        .ppm-label {{
            text-align: center;
            color: #888;
            font-size: 0.9em;
            margin-top: 4px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}
        .info-box {{
            background: #2a2a2a;
            border-radius: 12px;
            padding: 14px;
            text-align: center;
        }}
        .info-label {{
            color: #888;
            font-size: 0.8em;
            margin-bottom: 6px;
        }}
        .info-value {{
            font-size: 1.4em;
            font-weight: bold;
            color: white;
        }}
        .gauge-wrap {{
            background: #2a2a2a;
            border-radius: 8px;
            height: 24px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .gauge-bar {{
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #ffff00, #ff3333);
            border-radius: 8px;
            transition: width 0.5s;
            width: {min(100, int((ppm/300)*100))}%;
        }}
        .forecast {{
            text-align: center;
            font-size: 1.1em;
            padding: 10px;
            color: #ccc;
        }}
        .graph-wrap {{
            display: flex;
            align-items: flex-end;
            height: 80px;
            gap: 4px;
            padding-top: 10px;
        }}
        .bar {{
            flex: 1;
            background: {color};
            border-radius: 4px 4px 0 0;
            opacity: 0.8;
        }}
        .update-time {{
            text-align: center;
            color: #555;
            font-size: 0.75em;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <h1>🔥 가스누출 경보 시스템</h1>

    <!-- 상태 카드 -->
    <div class="card status-card">
        <div class="status-text">{status_kr}</div>
    </div>

    <!-- 현재 PPM -->
    <div class="card">
        <div class="ppm-big">{ppm:.1f}</div>
        <div class="ppm-label">PPM (현재 농도)</div>
        <div class="gauge-wrap">
            <div class="gauge-bar"></div>
        </div>
    </div>

    <!-- 정보 그리드 -->
    <div class="grid" style="margin-bottom:16px">
        <div class="info-box">
            <div class="info-label">🏆 최고 PPM</div>
            <div class="info-value">{peak:.1f}</div>
        </div>
        <div class="info-box">
            <div class="info-label">⚠️ 경고 횟수</div>
            <div class="info-value">{warns}회</div>
        </div>
        <div class="info-box">
            <div class="info-label">🕐 측정 시간</div>
            <div class="info-value" style="font-size:1.1em">{elapsed}</div>
        </div>
        <div class="info-box">
            <div class="info-label">📊 공기질 예보</div>
            <div class="info-value" style="font-size:1em">{forecast}</div>
        </div>
    </div>

    <!-- 그래프 -->
    <div class="card">
        <div style="color:#888; font-size:0.85em; margin-bottom:6px">
            📈 최근 PPM 변화 (20회)
        </div>
        <div class="graph-wrap" id="graph">
"""
    # 막대 그래프
    max_val = max(log) if log else 1
    for v in log:
        h = int((v / max_val) * 100) if max_val > 0 else 0
        html += f'            <div class="bar" style="height:{h}%"></div>\n'

    html += f"""        </div>
    </div>

    <div class="update-time">3초마다 자동 갱신</div>
</body>
</html>"""
    return html

# ================================
# JSON 데이터 응답
# ================================
def get_json(ppm, status, peak, warns, elapsed, forecast):
    data = {{
        "ppm"      : round(ppm, 1),
        "status"   : status,
        "peak"     : round(peak, 1),
        "warns"    : warns,
        "elapsed"  : elapsed,
        "forecast" : forecast
    }}
    return json.dumps(data)

# ================================
# 웹서버
# ================================
def start_server(ip):
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    s    = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    s.setblocking(False)
    print(f"🌐 웹서버 시작! → http://{ip}")
    return s

# ================================
# 메인
# ================================
def main():
    global warn_count, peak_ppm

    # 워밍업
    print("=" * 40)
    print("  가스누출 경보 위험도 시각화 시스템")
    print("  워밍업 중... (20초)")
    print("=" * 40)
    for i in range(20, 0, -1):
        set_color(50, 50, 50)
        time.sleep(0.3)
        led_off()
        time.sleep(0.3)
        print(f"  워밍업 남은 시간 : {i}초")
    led_off()

    # 와이파이 연결
    ip = connect_wifi()
    if not ip:
        print("와이파이 없이 실행!")
        ip = "0.0.0.0"

    # 웹서버 시작
    server = start_server(ip)

    prev_status = "안전"

    while True:
        # 센서 읽기
        raw_value = mq2.read_u16()
        ppm       = convert_to_ppm(raw_value)
        status    = get_status(ppm)
        forecast  = get_forecast(ppm)

        update_peak(ppm)
        update_warn_count(ppm, prev_status)
        update_log(ppm)

        # 시리얼 출력
        print(f"PPM:{ppm:.1f} | {status} | 최고:{peak_ppm:.1f} | 경고:{warn_count}회")

        # LED 효과
        if ppm < SAFE_THRESHOLD:
            safe_mode(ppm)
        elif ppm < WARN_THRESHOLD:
            warning_mode(ppm)
        else:
            danger_mode(ppm)

        # 웹 요청 처리
        try:
            conn, addr = server.accept()
            conn.setblocking(True)
            request = conn.recv(1024).decode()

            if "/data" in request:
                # JSON 데이터 요청
                response = get_json(ppm, status, peak_ppm,
                                   warn_count, get_elapsed_time(), forecast)
                conn.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
                conn.send(response)
            else:
                # 웹페이지 요청
                html = get_html(ppm, status, peak_ppm,
                               warn_count, get_elapsed_time(),
                               forecast, ppm_log)
                conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
                conn.send(html)

            conn.close()
        except:
            pass

        prev_status = status

main()
