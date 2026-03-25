from django.urls import path
from .views import MCPWellKnownView

urlpatterns = [
    path('.well-known/mcp-server', MCPWellKnownView.as_view(), name='mcp-well-known'),
]
