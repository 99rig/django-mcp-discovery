import json
from django.http import HttpResponse
from django.views import View
from .manifest import build_manifest


class MCPWellKnownView(View):
    """
    Serves /.well-known/mcp-server as JSON.
    Implements draft-serra-mcp-discovery-uri.
    """

    def get(self, request, *args, **kwargs):
        manifest = build_manifest()

        response = HttpResponse(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            content_type='application/json; charset=utf-8',
        )
        response['Cache-Control'] = 'max-age=3600, public'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET'
        response['X-MCP-Discovery'] = 'draft-serra-mcp-discovery-uri-04'
        return response
