import json
from pathlib import Path
from django import template
from sitecontent.models import MediaAsset

register = template.Library()
ASSET_MAP = Path(__file__).resolve().parents[1] / "legacy_asset_urls.json"


@register.filter
def asset_url(filename):
    """Resolve an existing asset descriptor to its original URL."""
    if not filename:
        return ""
    if str(filename).startswith(("/", "http://", "https://")):
        return filename
    upload = MediaAsset.objects.filter(legacy_filename=filename, is_visible=True).exclude(file="").first()
    if upload:
        return upload.url
    try:
        return json.loads(ASSET_MAP.read_text(encoding="utf-8")).get(filename, "")
    except (OSError, json.JSONDecodeError):
        return ""


@register.filter
def get_item(mapping, key):
    return mapping.get(key) if mapping else None


@register.filter
def paragraphs(value):
    if not value:
        return []
    return [part.strip() for part in str(value).split("\n\n") if part.strip()]
