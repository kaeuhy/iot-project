import RPi.GPIO as GPIO
import spidev
import time
import random

# 핀 번호 설정
button_pin = 17
buzzer_pin = 18
led_red_pin = 22
led_green_pin = 23
light_sensor_channel = 0  # 조도센서가 연결된 MCP3208의 채널 번호

# SPI 설정 (조도센서 읽기용)
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.setup(led_red_pin, GPIO.OUT)
GPIO.setup(led_green_pin, GPIO.OUT)

# PWM 만들기 (소리, 불빛 조절)
buzzer = GPIO.PWM(buzzer_pin, 1000)
led_red = GPIO.PWM(led_red_pin, 1000)
led_green = GPIO.PWM(led_green_pin, 1000)

# 처음에는 다 끈 상태로 시작
buzzer.start(0)
led_red.start(0)
led_green.start(0)

# 버튼이 눌릴 때까지 기다리는 함수
def wait_for_button():
    while GPIO.input(button_pin) == GPIO.HIGH:
        time.sleep(0.01)
    while GPIO.input(button_pin) == GPIO.LOW:
        time.sleep(0.01)

# 조도센서에서 숫자값을 읽는 함수
def read_light():
    value = spi.xfer2([6 | (light_sensor_channel >> 2), (light_sensor_channel & 3) << 6, 0])
    light_level = ((value[1] & 15) << 8) | value[2]
    return light_level

# 반응이 느릴 때 불빛과 부저로 경고하기
def blink_led_and_buzzer():
    light = read_light()
    is_dark = light < 300

    print(f"Light level: {light} → {'Dark' if is_dark else 'Bright'}")

    buzzer.ChangeDutyCycle(50)

    for i in range(5):
        if is_dark:
            led_red.ChangeDutyCycle(20)
            led_green.ChangeDutyCycle(0)
        else:
            led_red.ChangeDutyCycle(100)
            led_green.ChangeDutyCycle(0)

        time.sleep(0.3)

        if is_dark:
            led_red.ChangeDutyCycle(0)
            led_green.ChangeDutyCycle(20)
        else:
            led_red.ChangeDutyCycle(0)
            led_green.ChangeDutyCycle(100)

        time.sleep(0.3)

    buzzer.ChangeDutyCycle(0)
    led_red.ChangeDutyCycle(0)
    led_green.ChangeDutyCycle(0)

# 반응 속도 테스트
def start_test():
    print("\n[Reaction Test Started]")
    slow_reaction_count = 0

    for round_number in range(3):
        wait_seconds = random.uniform(1, 5)
        print(f"\nRound {round_number + 1}: Waiting for {wait_seconds:.2f} seconds...")
        time.sleep(wait_seconds)

        print("Buzzer ON! Press the button!")
        buzzer.ChangeDutyCycle(50)
        start_time = time.time()

        wait_for_button()

        end_time = time.time()
        buzzer.ChangeDutyCycle(0)

        reaction_time = end_time - start_time
        print(f"Reaction time: {reaction_time:.3f} seconds")

        if reaction_time > 0.5:
            slow_reaction_count += 1

    print("\n[Result]")
    if slow_reaction_count >= 2:
        print("Too slow! You might be sleepy. Please take a break.")
        blink_led_and_buzzer()
    else:
        print("Good reaction. No sign of sleepiness.")

# 프로그램 시작
try:
    print("Welcome! Press the button to start the reaction test.")

    while True:
        wait_for_button()
        start_test()

except KeyboardInterrupt:
    print("Program stopped by user.")

finally:
    buzzer.stop()
    led_red.stop()
    led_green.stop()
    GPIO.cleanup()
    spi.close()
