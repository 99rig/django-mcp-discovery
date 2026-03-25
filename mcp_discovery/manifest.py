from django.conf import settings
from django.utils import timezone


def _validate_endpoint_domain(endpoint, site_url):
    """
    Security: endpoint host MUST match or be subdomain of site host.
    draft-serra-mcp-discovery-uri-02 Section 6.8
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
    Implements draft-serra-mcp-discovery-uri-02.
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

    auth_type = config.get('AUTH', 'none')
    manifest['auth'] = {'type': auth_type}

    capabilities = config.get('CAPABILITIES', ['tools', 'resources'])
    manifest['capabilities'] = capabilities

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
