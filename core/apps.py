from django.apps import AppConfig
import paho.mqtt.client as mqtt
import json
import environ

env = environ.Env()


class CoreConfig(AppConfig):
    name = 'core'


def set_light(state):
    # print("creating new instance")
    client = mqtt.Client("dash")  # create new instance

    client.username_pw_set(username=env('MQTT_USER'), password=env('MQTT_PWD'))
    client.connect(env('MQTT_HOST'))  # connect to broker
    print("Connected")
    client.loop_start()  # start the loop
    print('Loop started')
    gateway = "+/#"
    client.subscribe(gateway)

    if state:
        client.publish('home/room/lights/main-light/cmnd/POWER', 'ON')
    else:
        client.publish('home/room/lights/main-light/cmnd/POWER', 'OFF')

    client.loop_stop() #stop the loop


def persiana(state):
    # print("creating new instance")
    client = mqtt.Client("dash")  # create new instance

    client.username_pw_set(username=env('MQTT_USER'), password=env('MQTT_PWD'))
    client.connect(env('MQTT_HOST'))  # connect to broker
    print("Connected")
    client.loop_start()  # start the loop
    print('Loop started')
    gateway = "+/#"
    client.subscribe(gateway)
    print('going ',state)
    msg = dict(value=state)
    msg = json.dumps(msg)
    client.publish('home/room/persiana', msg)

    client.loop_stop() #stop the loop

def hvac(state):
    client = mqtt.Client("dash")  # create new instance

    client.username_pw_set(username=env('MQTT_USER'), password=env('MQTT_PWD'))
    client.connect(env('MQTT_HOST'))  # connect to broker
    print("Connected")
    client.loop_start()  # start the loop
    print('Loop started')
    gateway = "+/#"
    client.subscribe(gateway)
    print('going ', state)
    msg = dict()
    if state == 'off':
        msg['power'] = 'off'

    elif state == 'on':
        msg['power'] = 'cold'
        msg['temp'] = 18

    msg = json.dumps(msg)
    client.publish('home/room/hvac', msg)
