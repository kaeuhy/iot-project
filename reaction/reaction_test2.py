import RPi.GPIO as GPIO
import time
import random
import threading
import Adafruit_DHT

# --- 핀 설정 ---
BUTTON_PIN = 17
BUZZER_PIN = 18
DHT_PIN = 4  # DHT 센서 GPIO (보드 상 위치 확인 필요)

# --- GPIO 초기화 ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# --- 부저 PWM 설정 ---
pwm = GPIO.PWM(BUZZER_PIN, 1000)  # 1kHz tone

# --- 전역 변수 ---
reaction_times = []
running_test = False  # 반응속도 테스트 중인지 체크용

# --- 온도 측정 쓰레드 ---
def temperature_monitor():
    sensor = Adafruit_DHT.DHT11
    while True:
        if not running_test:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, DHT_PIN)
            if temperature is not None:
                print(f"[Temp] Current temp: {temperature:.1f}°C")
                if temperature < 21:
                    print("Increase the temperature.")
                elif temperature > 23:
                    print("Decrease the temperature.")
                else:
                    print("Keep the temperature.")
            else:
                print("[Temp] Failed to read sensor.")
        time.sleep(3)

# --- 버튼 대기 함수 ---
def wait_for_button_press():
    while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        time.sleep(0.01)
    while GPIO.input(BUTTON_PIN) == GPIO.LOW:
        time.sleep(0.01)

# --- 반응속도 테스트 실행 함수 ---
def run_test():
    global running_test
    running_test = True  # 온도 측정 멈추기

    print("Start the drowsy driving test.")
    reaction_times.clear()
    slow_reactions = 0

    for i in range(3):
        wait_time = random.uniform(1, 5)
        print(f"\nRound {i+1}: Wait for {wait_time:.2f} seconds...")
        time.sleep(wait_time)

        print("Buzzer ON! React now!")
        pwm.start(50)
        start_time = time.time()

        wait_for_button_press()

        end_time = time.time()
        pwm.stop()

        reaction_time = end_time - start_time
        reaction_times.append(reaction_time)

        print(f"Your reaction time: {reaction_time:.3f} seconds")

        if reaction_time > 0.5:
            slow_reactions += 1

    print("\nTest Result:")
    if slow_reactions >= 2:
        print("Drowsy driving is suspected. Take a break.")
    else:
        print("It's not drowsy driving yet.")

    running_test = False  # 온도 측정 재개

# --- 메인 실행 ---
try:
    print("System ready. Monitoring temperature...")
    
    # 온도 측정 쓰레드 시작
    temp_thread = threading.Thread(target=temperature_monitor)
    temp_thread.daemon = True
    temp_thread.start()

    # 메인 루프: 버튼 누를 때마다 테스트 실행
    while True:
        print("\n[System] Press the button to start the test.")
        wait_for_button_press()
        run_test()

except KeyboardInterrupt:
    print("Exiting program.")

finally:
    pwm.stop()
    GPIO.cleanup()
