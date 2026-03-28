from django.conf import settings
from django.utils import timezone


# Lista globale dei tool preview registrati runtime (django-mcp-server integration)
_tool_previews = []


def update_tools_preview(tool: dict):
    """
    Called by django-mcp-server when a tool is registered via @mcp_tool.
    Adds the tool to the runtime tools_preview list.

    Args:
        tool: dict with at minimum {"name": str, "description": str}
    """
    global _tool_previews
    # Avoid duplicates
    if not any(t.get("name") == tool.get("name") for t in _tool_previews):
        _tool_previews.append(tool)


def _validate_endpoint_domain(endpoint, site_url):
    """
    Security: endpoint host MUST match or be subdomain of site host.
    draft-serra-mcp-discovery-uri-04 Section 6.8
    """
    from urllib.parse import urlparse
    if not endpoint or not site_url:
        return True
    site_host = urlparse(site_url).hostname or ''
    endpoint_host = urlparse(endpoint).hostname or ''
    if not endpoint_host or not site_host:
        return True
    return endpoint_host == site_host or endpoint_host.endswith('.' + site_host)


def build_manifest():
    """
    Build the MCP manifest dict from Django settings.
    All fields are optional except mcp_version, name, endpoint, transport.
    Implements draft-serra-mcp-discovery-uri-04.
    """
    config = getattr(settings, 'MCP_DISCOVERY', {})

    # Required fields
    site_url = getattr(settings, 'SITE_URL', None)
    custom_endpoint = config.get('ENDPOINT')
    if custom_endpoint and not _validate_endpoint_domain(custom_endpoint, site_url or _get_default_endpoint()):
        # Security: reject endpoint on unrelated domain, fall back to default
        custom_endpoint = None
    manifest = {
        'mcp_version': '2025-06-18',
        'name': config.get('NAME', _get_site_name()),
        'endpoint': custom_endpoint or _get_default_endpoint(),
        'transport': config.get('TRANSPORT', 'http'),
    }

    # SHOULD fields
    description = config.get('DESCRIPTION', '')
    if description:
        manifest['description'] = description

    # Auth — draft-04 new structured format
    auth_config = config.get('AUTH', {})
    if isinstance(auth_config, str):
        # Retrocompatibility: AUTH = 'none' | 'apikey' | 'oauth2'
        auth_config = {'required': False, 'methods': [auth_config]}

    auth_obj = {
        'required': auth_config.get('required', False),
        'methods': auth_config.get('methods', ['none']),
    }
    # endpoint required if methods includes 'bearer' or 'oauth2'
    if any(m in auth_obj['methods'] for m in ('bearer', 'oauth2')):
        endpoint = auth_config.get('endpoint')
        if endpoint:
            auth_obj['endpoint'] = endpoint
    # scopes required if oauth2
    if 'oauth2' in auth_obj['methods']:
        scopes = auth_config.get('scopes', [])
        if scopes:
            auth_obj['scopes'] = scopes

    manifest['auth'] = auth_obj

    capabilities = config.get('CAPABILITIES', ['tools', 'resources'])
    manifest['capabilities'] = capabilities

    # trust_class — draft-04 new field
    trust_class = config.get('TRUST_CLASS', None)
    if trust_class:
        manifest['trust_class'] = trust_class

        # sandbox: expires REQUIRED
        if trust_class == 'sandbox':
            from datetime import timedelta
            expires_days = config.get('EXPIRES_DAYS', 30)
            manifest['expires'] = (timezone.now() + timedelta(days=expires_days)).isoformat()

        # regulated: compliance + logging + cache_ttl REQUIRED
        if trust_class == 'regulated':
            compliance = config.get('COMPLIANCE', {})
            if not compliance.get('jurisdiction'):
                raise ValueError(
                    "MCP_DISCOVERY: trust_class='regulated' requires "
                    "COMPLIANCE = {'jurisdiction': 'EU', ...}"
                )
            manifest['compliance'] = compliance

            logging_config = config.get('LOGGING', {'required': True})
            manifest['logging'] = logging_config

            manifest['cache_ttl'] = config.get('CACHE_TTL', 300)

    # cache_ttl — draft-04 MAY for all (regulated already handled above)
    if trust_class != 'regulated':
        cache_ttl = config.get('CACHE_TTL', None)
        if cache_ttl:
            manifest['cache_ttl'] = cache_ttl

    # MAY fields
    categories = config.get('CATEGORIES', [])
    if categories:
        manifest['categories'] = categories

    languages = config.get('LANGUAGES', _get_languages())
    if languages:
        manifest['languages'] = languages

    contact = config.get('CONTACT', '')
    if contact:
        manifest['contact'] = contact

    docs = config.get('DOCS', '')
    if docs:
        manifest['docs'] = docs

    manifest['last_updated'] = timezone.now().isoformat()
    manifest['crawl'] = config.get('CRAWL', True)

    # Primitive previews (MAY) — draft-serra-mcp-discovery-uri-04 Section 6.10
    for key in ('TOOLS_PREVIEW', 'RESOURCES_PREVIEW', 'PROMPTS_PREVIEW'):
        value = config.get(key)
        if value is not None:
            manifest[key.lower()] = value

    # Runtime tool previews from django-mcp-server (if not already configured statically)
    if 'tools_preview' not in manifest and _tool_previews:
        manifest['tools_preview'] = _tool_previews

    return manifest


def _get_site_name():
    """Try to get site name from Django sites framework or settings."""
    try:
        from django.contrib.sites.models import Site
        return Site.objects.get_current().name + ' MCP Server'
    except Exception:
        pass
    return getattr(settings, 'SITE_NAME', 'MCP Server')


def _get_default_endpoint():
    """Build default endpoint URL from SITE_URL or ALLOWED_HOSTS."""
    site_url = getattr(settings, 'SITE_URL', None)
    if site_url:
        return site_url.rstrip('/') + '/mcp/'

    allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
    host = next((h for h in allowed_hosts if h not in ('*', 'localhost', '127.0.0.1')), None)
    if host:
        return f'https://{host}/mcp/'

    return 'https://example.com/mcp/'


def _get_languages():
    """Get language code from Django LANGUAGE_CODE setting."""
    lang = getattr(settings, 'LANGUAGE_CODE', 'en')
    # e.g. it-it → it, en-us → en
    return [lang.split('-')[0].split('_')[0].lower()]
