import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Dato, Connection
from .apps import set_light, persiana


class DataConsumer(WebsocketConsumer):
    def connect(self):
        self.loc_name = self.scope['url_route']['kwargs']['loc_name']
        self.loc_group_name = 'livedata'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.loc_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.loc_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        type = text_data_json['type']
        if type == 'data_update':
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.loc_group_name,
                {
                    'type': 'data_update',
                    'message': message,
                    'sensor': self.loc_name,
                })

    def data_update(self, event):
        message = event['message']
        if self.loc_name == 'NB':
            message = "{:.2f}".format(float(message) * 10 * 950 / (1024 * 100))

        try:
            dato = Dato.objects.get(location=self.loc_name)
            dato.valor = message
            dato.save()
        except Dato.DoesNotExist:
            dato = Dato()
            dato.location = self.loc_name
            dato.valor = message
            dato.save()
        except Exception as e:
            print(repr(e))

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'sensor': event['sensor'],
            'message': message
        }))


class CommandConsumer(WebsocketConsumer):
    def connect(self):
        self.thing = self.scope['url_route']['kwargs']['thing']
        self.thing_group_name = 'control'
        try:
            headers = dict(self.scope['headers'])
            try:
                con = Connection(origin=headers[b'x-real-ip'])
            except KeyError:
                con = Connection(origin=headers[b'host'])
            con.save()
        except Exception as e:
            raise Exception('what '+repr(e) + str(headers))
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.thing_group_name,
            self.channel_name
        )
        self.accept()


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.thing_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        print('received message')
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            type = text_data_json['type']
            apikey = text_data_json['apikey']
            thing = text_data_json['thing']
            if apikey != '6c6cb21d-218e-4f80-8c0b-715547bdcbe4':
                return
        except Exception as e:
            raise Exception(repr(e))
        print('apikey ok')
        if type == 'command':
            print('type ok')
            if thing == 'light':
                print('touching lights!')
                if message == 'on':
                    set_light(True)
                elif message == 'off':
                    set_light(False)
            elif thing == 'persiana':
                if message == 'up':
                    persiana('up')
                elif message == 'stop':
                    persiana('stop')
                elif message == 'down':
                    persiana('down')

        async_to_sync(self.channel_layer.group_send)(
            self.thing_group_name,
            {
                'type': 'data_update',
                'command': message,
                'thing': thing,
            })

    def data_update(self, event):
        message = event['command']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'sensor': event['thing'],
            'message': message
        }))
