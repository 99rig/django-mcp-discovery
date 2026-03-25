from django.apps import AppConfig

class MCPDiscoveryConfig(AppConfig):
    name = 'mcp_discovery'
    verbose_name = 'MCP Discovery'

    def ready(self):
        pass
