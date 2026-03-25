# django-mcp-discovery

Exposes `/.well-known/mcp-server` on your Django project so AI agents
can discover it via `mcp://`. Implements
[draft-serra-mcp-discovery-uri-03](https://datatracker.ietf.org/doc/draft-serra-mcp-discovery-uri/).

## Installation

```bash
pip install django-mcp-discovery
```

## Setup

**1. Add to INSTALLED_APPS:**

```python
INSTALLED_APPS = [
    ...
    'mcp_discovery',
]
```

**2. Include URLs:**

```python
urlpatterns = [
    ...
    path('', include('mcp_discovery.urls')),
]
```

**3. Done.** Visit `https://yoursite.com/.well-known/mcp-server`.

## Configuration (optional)

```python
MCP_DISCOVERY = {
    'NAME':             'My Site MCP Server',
    'ENDPOINT':         'https://mysite.com/mcp/',
    'DESCRIPTION':      'Natural language description of the server',
    'AUTH':             'none',         # none | apikey | oauth2
    'CAPABILITIES':     ['tools', 'resources'],
    'CATEGORIES':       ['e-commerce', 'fashion'],
    'LANGUAGES':        ['it', 'en'],
    'CONTACT':          'api@mysite.com',
    'DOCS':             'https://mysite.com/mcp/docs/',
    'EXPIRES_DAYS':     90,             # manifest expiry in days
    'CRAWL':            True,           # False to opt out of indexing

    # Optional — primitive previews (draft-03 Section 6.10)
    # Use a list for static tools, or 'dynamic' for dynamic ones
    'TOOLS_PREVIEW': [
        {'name': 'search_products', 'description': 'Search by category'},
        {'name': 'check_stock',     'description': 'Real-time availability'},
    ],
    'RESOURCES_PREVIEW': 'dynamic',
    'PROMPTS_PREVIEW':   'dynamic',
}
```

Auto-detected if not set:
- **Name** — from `django.contrib.sites` or `SITE_NAME` setting
- **Endpoint** — from `SITE_URL` or first non-localhost `ALLOWED_HOSTS`
- **Language** — from `LANGUAGE_CODE` setting

## Example output

Minimal (no configuration):

```json
{
  "mcp_version": "2025-06-18",
  "name": "My Shop MCP Server",
  "endpoint": "https://myshop.com/mcp/",
  "transport": "http",
  "auth": { "type": "none" },
  "capabilities": ["tools", "resources"],
  "languages": ["it"],
  "last_updated": "2026-03-25T00:00:00+00:00",
  "expires": "2026-09-23T00:00:00+00:00",
  "crawl": true
}
```

With `tools_preview` (draft-03 Section 6.10):

```json
{
  "mcp_version": "2025-06-18",
  "name": "My Shop MCP Server",
  "endpoint": "https://myshop.com/mcp/",
  "transport": "http",
  "auth": { "type": "none" },
  "capabilities": ["tools", "resources"],
  "categories": ["e-commerce"],
  "languages": ["it"],
  "expires": "2026-09-23T00:00:00+00:00",
  "crawl": true,
  "tools_preview": [
    {
      "name": "search_products",
      "description": "Search products by category and material"
    },
    {
      "name": "check_stock",
      "description": "Check real-time warehouse availability"
    }
  ],
  "resources_preview": "dynamic",
  "prompts_preview": "dynamic"
}
```

## Security

- **Endpoint domain validation** — custom endpoint MUST be on same
  domain or subdomain. Invalid endpoints fall back to default.
  (draft-03 Section 6.8)
- **Expires field** — manifest declares its own expiry date.
  (draft-03 Section 6.9)

## Changelog

### v0.3.0
- Added `tools_preview`, `resources_preview`, `prompts_preview` fields (draft-03 Section 6.10)
- Use a list for static previews, or 'dynamic' for dynamic ones

### v0.2.0
- Security: endpoint domain validation (Section 6.8)
- Security: `expires` field with `EXPIRES_DAYS` setting (Section 6.9)

### v0.1.0
- Initial release

## Links

- [mcpstandard.dev](https://mcpstandard.dev) — specification
- [IETF Draft -03](https://datatracker.ietf.org/doc/draft-serra-mcp-discovery-uri/03/)
- [GitHub Discussion #2462](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2462)
- [WordPress plugin](https://github.com/99rig/mcp-wordpress)

## Author

Mumble Group — Milan, Italy — support@mumble.group
