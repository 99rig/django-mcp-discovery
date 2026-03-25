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
    'NAME':        'My Site MCP Server',
    'ENDPOINT':    'https://mysite.com/mcp/',
    'DESCRIPTION': 'Natural language description of the server',
    'AUTH':        'none',           # none | apikey | oauth2
    'CAPABILITIES': ['tools', 'resources'],
    'CATEGORIES':  ['e-commerce', 'fashion'],
    'LANGUAGES':   ['it', 'en'],
    'CONTACT':     'api@mysite.com',
    'DOCS':        'https://mysite.com/mcp/docs/',
    'EXPIRES_DAYS': 90,              # manifest expiry in days
    'CRAWL':       True,             # False to opt out of indexing
}
```

Auto-detected if not set:
- **Name** — from `django.contrib.sites` or `SITE_NAME` setting
- **Endpoint** — from `SITE_URL` or first non-localhost `ALLOWED_HOSTS`
- **Language** — from `LANGUAGE_CODE` setting

## Example output

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
  "last_updated": "2026-03-25T00:00:00+00:00",
  "expires": "2026-09-23T00:00:00+00:00",
  "crawl": true
}
```

## Security

- **Endpoint domain validation** — custom endpoint MUST be on same
  domain or subdomain of your site. Invalid endpoints fall back to
  default. (draft-03 Section 6.8)
- **Expires field** — manifest declares its own expiry date so clients
  know when to re-fetch. (draft-03 Section 6.9)

## Changelog

### v0.2.0
- Security: endpoint domain validation
- Security: `expires` field with configurable `EXPIRES_DAYS`

### v0.1.0
- Initial release

## Links

- [mcpstandard.dev](https://mcpstandard.dev) — specification
- [IETF Draft -03](https://datatracker.ietf.org/doc/draft-serra-mcp-discovery-uri/03/)
- [GitHub Discussion #2462](https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/2462)
- [WordPress plugin](https://github.com/99rig/mcp-wordpress)

## Author

Mumble Group — Milan, Italy — support@mumble.group
