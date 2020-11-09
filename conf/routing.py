from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
import core.routing
# from django.conf.urls import url
# from django_plotly_dash.routing import http_routes
# from django_plotly_dash.consumers import MessageConsumer
# from django_plotly_dash.util import pipe_ws_endpoint_name
from core import consumers

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                core.routing.websocket_urlpatterns
      #       +   [url(pipe_ws_endpoint_name(), MessageConsumer),]
            ),
        )
    ),
    #'http':AuthMiddlewareStack(URLRouter(http_routes)),
    "channel": ChannelNameRouter({
        "T": consumers.DataConsumer,
        "H": consumers.DataConsumer,
        "TO": consumers.DataConsumer,
        "HO": consumers.DataConsumer,
        "P1": consumers.DataConsumer,
        "P2": consumers.DataConsumer,
        "P3": consumers.DataConsumer,
        "NB": consumers.DataConsumer,
        "light": consumers.CommandConsumer,
    }),
})


