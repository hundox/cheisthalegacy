import json
from functools import lru_cache
from pathlib import Path
from django.db.models import Q

from .models import Chapter, Initiative, MediaAsset

MANIFEST = Path(__file__).with_name("legacy_media.json")


@lru_cache(maxsize=1)
def media_manifest():
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"chapters": {}, "primary": {}, "satellites": {}, "groups": {}}


def photos_for(slug):
    uploaded = list(MediaAsset.objects.filter(chapter__slug=slug, role="chapter_gallery", is_visible=True).exclude(file="").order_by("order", "id"))
    if uploaded:
        return [{"filename": item.url, "alt": item.alt_text, "kind": item.kind} for item in uploaded]
    return media_manifest()["chapters"].get(slug, [])


def initiative_gallery(slug):
    media = media_manifest()
    group_slugs = [entry["slug"] for entry in media["groups"].get(slug, [])] or [slug]
    return [photo for current in group_slugs for photo in ([media["primary"][current]] if current in media["primary"] else []) + media["satellites"].get(current, []) if photo.get("kind") != "video"]


def initiative_mosaics(slug):
    media = media_manifest()
    groups = media["groups"].get(slug, [{"label": "Moments from the initiative", "slug": slug}])
    result = []
    for group in groups:
        assets = MediaAsset.objects.filter(initiative__slug=slug, is_visible=True).exclude(file="")
        group_filter = Q(collection_key=group["slug"])
        if group["slug"] == slug:
            group_filter |= Q(collection_key="")
        uploaded = list(assets.filter(group_filter).order_by("order", "slot", "id"))
        primary_asset = next((item for item in uploaded if item.role == "initiative_primary"), None)
        satellites_asset = [item for item in uploaded if item.role == "initiative_satellite"]
        satellites = ([{"filename": item.url, "alt": item.alt_text, "kind": item.kind} for item in satellites_asset]
                      if satellites_asset else media["satellites"].get(group["slug"], []))
        result.append({
            **group,
            "primary": ({"filename": primary_asset.url, "alt": primary_asset.alt_text, "kind": primary_asset.kind}
                        if primary_asset else media["primary"].get(group["slug"])),
            "satellites": satellites,
            "expanded": len(satellites) > 5,
            "left": satellites[::2],
            "right": satellites[1::2],
            "slots": satellites if satellites else [None, None, None, None],
        })
    return result


def life_gallery_entries():
    media = media_manifest()
    result = []
    for chapter in Chapter.objects.filter(is_published=True).order_by("kind", "order", "id"):
        uploaded = list(MediaAsset.objects.filter(chapter=chapter, role="chapter_gallery", is_visible=True).exclude(file="").order_by("order", "id"))
        photos = ([{"filename": item.url, "alt": item.alt_text, "kind": item.kind} for item in uploaded]
                  if uploaded else media["chapters"].get(chapter.slug, []))
        if photos:
            result.append({"slug": chapter.slug, "title": chapter.title, "photos": photos})
    return result


def initiative_gallery_entries():
    result = []
    for item in Initiative.objects.filter(is_published=True):
        photos = initiative_gallery(item.slug)
        uploaded = list(MediaAsset.objects.filter(initiative__slug=item.slug, is_visible=True).exclude(file="").order_by("order", "slot", "id"))
        if uploaded:
            photos = [{"filename": asset.url, "alt": asset.alt_text, "kind": asset.kind}
                      for asset in uploaded if asset.role in ("initiative_primary", "initiative_satellite") and asset.kind != "video"]
        if photos:
            result.append({"slug": item.slug, "title": item.title, "photos": photos})
    return result


def gallery_entries():
    return life_gallery_entries() + initiative_gallery_entries()
