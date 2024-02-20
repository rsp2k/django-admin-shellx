from django.urls import path, re_path

from . import consumers

app_name = "django_web_repl"

urlpatterns = []

websocket_urlpatterns = [
    re_path(r"ws/terminal/(?P<room_name>\w+)/$", consumers.TerminalConsumer.as_asgi()),
]
