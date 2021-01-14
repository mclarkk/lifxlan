import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import os
import re
import ifaddr
from lifxlan import LifxLAN, group, device, light
from time import  sleep
#pruebapara jugui
#pruebapara jugui22
MQTT_ADDRESS = '192.168.0.9' #rasp
MQTT_USER = 'DOMOTICANE' #user
MQTT_PASSWORD = 'DOMOTICANE'
MQTT_TOPIC = 'casa/cuarto/luzpub'
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PIN_BUTTON = 17 #pin 11 abrir()
PIN_BUTTON1 = 27 #pin 13 cerrar()
PIN_BUTTON2 = 5 #pin 29 sera persiana
PIN_BUTTON3 = 6 #pin 31 sera para la persiana
PIN_BUTTON4=16 #ESTE pin 36 sera para seleccionar focos
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(4, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup(5, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(6, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(16,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


RoAPin = 23    # pin16 DT
RoBPin = 22    # pin15 CLK
RoSPin = 24    # pin18 SW
GPIO.setup(RoAPin, GPIO.IN,pull_up_down=GPIO.PUD_UP)    # input mode
GPIO.setup(RoBPin, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(RoSPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
globalCounter1 = 0
globalCounter = 0
flag = 0
Last_RoB_Status = 0
Current_RoB_Status = 0
led_on = False
foco = LifxLAN()
#mq_launch = subprocess.Popen(['sudo','mosquitto'])
#print('return code launching mqtt server:',mq_launch.returncode)
def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    bandera2=0
    a = str(msg.payload)
    b = re.findall('[0-9]',a)
    number=str()
    for i in b:
        number = number + i
    number1=int(number)
    #c = int(b)
    #print(c)
    if number1 <= 65000:
        foco1.set_brightness(number1)
    elif number1 == 70000:
        foco1.set_brightness(65535)
    elif number1 == 71000:
        foco1.set_brightness(0)
    elif number1==72000:
        sleep(0.1)
        if bandera2==0:
           foco1=light.Light("D0:73:D5:5C:A7:DB","192.168.0.15")
           print("foco1 seleccionado")
           bandera2=1
        else:
           foco1=light.Light("D0:73:D5:5E:25:BD","192.168.0.8")
           print("foco 2 seleccionado")
           bandera2=0


    
def rotaryDeal(self):
        global flag
        global Last_RoB_Status
        global Current_RoB_Status
        global globalCounter
        global globalCounter1
        Last_RoB_Status = GPIO.input(RoBPin)
        if globalCounter1 == 1:
                globalCounter=0
                globalCounter1=0
        while(not GPIO.input(RoAPin)):
                Current_RoB_Status = GPIO.input(RoBPin)
                flag = 1
        if flag == 1:
                flag = 0
                if (Last_RoB_Status == 0) and (Current_RoB_Status == 1) and globalCounter<10:
                        globalCounter = globalCounter + 1
                        intensidad = 6500 * globalCounter
                        print ('Intensidad = ',intensidad)
                        foco1.set_brightness(intensidad)
                if (Last_RoB_Status == 1) and (Current_RoB_Status == 0) and globalCounter > 0:
                        globalCounter = globalCounter - 1
                        intensidad = 6500 * globalCounter
                        print ('Intensidad = ',intensidad)
                        foco1.set_brightness(intensidad)


def clear(ev=None):
        sleep(0.1)
        global bandera
        if bandera == 1:
          foco1.set_brightness(65535)
          bandera = 0
        else:
          foco1.set_brightness(0)
          bandera=1

def callback_button(PIN_BUTTON):
    global led_on
    led_on = not led_on
    GPIO.output(4, GPIO.HIGH if led_on else GPIO.LOW)
    os.system('mosquitto_pub -h localhost -t casa/cuarto/puerta -m 3')
    #foco.set_power_all_lights('on',rapid=True)
def callback_button2(PIN_BUTTON1):
    global led_on
    led_on = not led_on
    GPIO.output(4, GPIO.HIGH if led_on else GPIO.LOW)
    os.system('mosquitto_pub -h localhost -t casa/cuarto/puerta -m 4')
def callback_button3(PIN_BUTTON2):
    sleep(0.1)
    if GPIO.input(5)==0:
       os.system('mosquitto_pub -h localhost -t casa/cuarto/persiana -m 1')
    elif GPIO.input(5)==1:
       os.system('mosquitto_pub -h localhost -t casa/cuarto/persiana -m 3')
def callback_button4(PIN_BUTTON3):
    sleep(0.1)
    if GPIO.input(6)==0:
       os.system('mosquitto_pub -h localhost -t casa/cuarto/persiana -m 2')
    elif GPIO.input(6)==1:
       os.system('mosquitto_pub -h localhost -t casa/cuarto/persiana -m 4')
def callback_button5(PIN_BUTTON4):
    sleep(0.1)
    global foco1
    global bandera1
    if bandera1==0:
       foco1=light.Light("D0:73:D5:5C:A7:DB","192.168.0.15")
       print("foco1 seleccionado")
       bandera1=1
    else:
       foco1=light.Light("D0:73:D5:5E:25:BD","192.168.0.8")
       print("foco 2 seleccionado")
       bandera1=0


GPIO.add_event_detect(5,  GPIO.BOTH, callback = callback_button3, bouncetime=400)
GPIO.add_event_detect(6,  GPIO.BOTH, callback = callback_button4, bouncetime=400)
GPIO.add_event_detect(17, GPIO.RISING, callback = callback_button, bouncetime=600)
GPIO.add_event_detect(27, GPIO.RISING, callback = callback_button2, bouncetime=600)
GPIO.add_event_detect(16, GPIO.RISING, callback = callback_button5,bouncetime=600)
#GPIO.cleanup()
def main():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    GPIO.add_event_detect(RoSPin, GPIO.FALLING, callback=clear) # wait for falling
    GPIO.add_event_detect(RoAPin, GPIO.RISING, callback=rotaryDeal) # wait for falling
    #rotaryDeal()
    try:
#             global globalCounter
             while True:
                    
                    mqtt_client.loop_forever()
    except KeyboardInterrupt: 
                    GPIO.cleanup()
    

bandera = 1
bandera1=0
intensidad = 0
seconds = 0


if __name__ == '__main__':
    GPIO.output(4, GPIO.HIGH)
    print('MQTT to InfluxDB bridge')
    main()

