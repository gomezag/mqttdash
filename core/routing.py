# chat/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/room/(?P<loc_name>\w+)/$', consumers.DataConsumer),
    re_path(r'ws/control/(?P<thing>\w+)/$', consumers.CommandConsumer),
]