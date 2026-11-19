from django.http import Http404
from django.shortcuts import render
from .data import GALLERIES
from .media_data import gallery_entries, initiative_gallery_entries, initiative_mosaics, life_gallery_entries, photos_for
from .models import Chapter, ContactDetail, FocusArea, Initiative, MediaAsset, PageSection, SitePage


def page(request, title, template, page_slug=None, **context):
    site_page = SitePage.objects.filter(slug=page_slug, is_published=True).first() if page_slug else None
    if page_slug and not site_page:
        raise Http404
    return render(request, template, {"page_title": site_page.title if site_page else title,
                                      "page_meta_description": site_page.meta_description if site_page else "",
                                      **context})


def chapter_rows(kind):
    return list(Chapter.objects.filter(kind=kind, is_published=True).order_by("order", "id"))


def home(request):
    quotes = list(MediaAsset.objects.filter(page__slug="home", role="quote", is_visible=True).exclude(file="").order_by("order", "id"))
    media = list(MediaAsset.objects.filter(page__slug="home", is_visible=True).exclude(file=""))
    hero = next((item.url for item in media if item.role == "hero"), None)
    poster = next((item.url for item in media if item.legacy_filename == "cheistha-portrait.jpeg"), None)
    journey = chapter_rows(Chapter.JOURNEY)
    for chapter in journey:
        chapter.card_photo = next(iter(photos_for(chapter.slug)), None)
    return page(request, "The Cheistha Kochhar Foundation | In Loving Memory", "sitecontent/home.html", page_slug="home",
                journey=journey, professional=chapter_rows(Chapter.PROFESSIONAL),
                quotes=quotes if quotes else range(24), hero_video_url=hero, hero_poster_url=poster)


def foundation(request):
    overview = PageSection.objects.filter(page__slug="foundation", key="overview").first()
    portrait_url = overview.image.url if overview and overview.image else None
    portrait_alt = overview.image_alt if overview else "Portrait of Cheistha Kochhar"
    return page(request, "The Foundation | The Cheistha Kochhar Foundation", "sitecontent/foundation.html", page_slug="foundation",
                initiatives=Initiative.objects.filter(is_published=True),
                focus_areas=FocusArea.objects.filter(is_visible=True), foundation_portrait_url=portrait_url, foundation_portrait_alt=portrait_alt)


def initiatives(request):
    return page(request, "Legacy in Action | The Cheistha Kochhar Foundation", "sitecontent/initiatives.html", page_slug="initiatives",
                initiatives=Initiative.objects.filter(is_published=True))


def initiative_detail(request, slug):
    item = Initiative.objects.filter(slug=slug, is_published=True).first()
    if not item:
        raise Http404
    items = list(Initiative.objects.filter(is_published=True))
    index = items.index(item)
    return page(request, f'{item.title} | The Cheistha Kochhar Foundation', "sitecontent/initiative_detail.html",
                item=item, paragraphs=item.description_paragraphs, back_url="/initiatives", back_label="All initiatives",
                mosaics=initiative_mosaics(slug), prev=items[index - 1] if index else None,
                next=items[index + 1] if index < len(items) - 1 else None)


def journey_detail(request, slug):
    return chapter_detail(request, slug, Chapter.JOURNEY, "/#journey", "Her formative years")


def chapter_detail(request, slug, kind, back_url, back_label):
    chapters = chapter_rows(kind)
    item = next((entry for entry in chapters if entry.slug == slug), None)
    if not item:
        raise Http404
    index = chapters.index(item)
    covers = {
        "centre-for-civil-society": ("centre-for-civil-society-logo.png", "Centre for Civil Society logo", None),
        "uidai": ("uidai-logo.png", "Aadhaar and Unique Identification Authority of India logo", None),
        "mckinsey": ("mckinsey-logo-marble.jpg", "McKinsey & Company signage on a marble wall", None),
        "planning-commission": ("planning-commission-logo.jpg", "Planning Commission, Government of India logo", None),
        "niti-aayog": ("niti-aayog-logo.webp", "NITI Aayog logo", None),
        "young-india-fellowship": ("ashoka-campus.png", "Ashoka University campus entrance gate", "ashoka-yif-logo.png"),
        "university-of-chicago": ("chicago-campus.webp", "University of Chicago campus and campus map", "chicago-shield.webp"),
        "london-school-of-economics": ("lse-campus.webp", "London School of Economics campus entrance and LSE sign", "lse-logo.png"),
    }
    cover_name, cover_alt, logo_name = covers.get(slug, (None, None, None))
    uploaded = list(item.media.filter(is_visible=True).order_by("order", "slot", "id"))
    uploaded = [asset for asset in uploaded if asset.file]
    cover_asset = next((asset for asset in uploaded if asset.role in ("chapter_cover", "chapter_identity")), None)
    if cover_asset:
        cover_name, cover_alt = cover_asset.url, cover_asset.alt_text
    return page(request, f'{item.title} | The Cheistha Kochhar Foundation', "sitecontent/chapter_detail.html",
                item=item, photos=photos_for(slug), cover_filename=cover_name, cover_alt=cover_alt,
                logo_filename=logo_name, back_url=back_url, back_label=back_label,
                prev=chapters[index - 1] if index else None,
                next=chapters[index + 1] if index < len(chapters) - 1 else None)


def professional(request):
    chapters = chapter_rows(Chapter.PROFESSIONAL)
    covers = {
        "centre-for-civil-society": ("centre-for-civil-society-logo.png", "Centre for Civil Society logo", None),
        "uidai": ("uidai-logo.png", "Aadhaar and UIDAI logo", None),
        "mckinsey": ("mckinsey-logo-marble.jpg", "McKinsey & Company signage on a marble wall", None),
        "planning-commission": ("planning-commission-logo.jpg", "Planning Commission logo", None),
        "niti-aayog": ("niti-aayog-logo.webp", "NITI Aayog logo", None),
        "young-india-fellowship": ("ashoka-campus.png", "Ashoka University campus", "ashoka-yif-logo.png"),
        "university-of-chicago": ("chicago-campus.webp", "University of Chicago campus", "chicago-shield.webp"),
        "london-school-of-economics": ("lse-campus.webp", "LSE campus", "lse-logo.png"),
    }
    for chapter in chapters:
        chapter.cover_filename, chapter.cover_alt, chapter.logo_filename = covers.get(chapter.slug, (None, None, None))
        uploaded = chapter.media.filter(role__in=("chapter_cover", "chapter_identity"), is_visible=True).exclude(file="").first()
        if uploaded:
            chapter.cover_filename, chapter.cover_alt = uploaded.url, uploaded.alt_text
    return page(request, "Professional Journey | The Cheistha Kochhar Foundation", "sitecontent/professional.html", page_slug="professional", chapters=chapters)


def professional_detail(request, slug):
    return chapter_detail(request, slug, Chapter.PROFESSIONAL, "/professional", "Professional journey")


def gallery(request):
    return page(request, "Gallery | The Cheistha Kochhar Foundation", "sitecontent/gallery.html", page_slug="gallery",
                life_collections=life_gallery_entries(), initiative_collections=initiative_gallery_entries())


def gallery_detail(request, slug):
    collection = next((entry for entry in gallery_entries() if entry["slug"] == slug), None)
    if not collection:
        raise Http404
    return page(request, f'{collection["title"]} | Gallery', "sitecontent/gallery_detail.html", collection=collection)


def timeline(request):
    return page(request, "Timeline | The Cheistha Kochhar Foundation", "sitecontent/timeline.html", page_slug="timeline",
                chapters=chapter_rows(Chapter.JOURNEY) + chapter_rows(Chapter.PROFESSIONAL))


def search(request):
    query = request.GET.get("q", "").strip()
    chapters = chapter_rows(Chapter.JOURNEY) + chapter_rows(Chapter.PROFESSIONAL)
    entries = [{"title": c.title, "kind": "Her Journey" if c.kind == Chapter.JOURNEY else "Professional Journey",
                "url": f'/{c.kind}/{c.slug}'} for c in chapters]
    entries += [{"title": g["title"], "kind": "Gallery", "url": f'/gallery/{g["slug"]}'} for g in GALLERIES]
    entries += [{"title": "Timeline", "kind": "Page", "url": "/timeline"}, {"title": "Contact", "kind": "Page", "url": "/contact"}]
    results = [e for e in entries if not query or query.casefold() in f'{e["title"]} {e["kind"]}'.casefold()]
    return page(request, "Search | The Cheistha Kochhar Foundation", "sitecontent/search.html", page_slug="search", query=query, results=results)


def contact(request):
    return page(request, "Foundation Information | The Cheistha Kochhar Foundation", "sitecontent/contact.html", page_slug="contact",
                contacts=ContactDetail.objects.filter(is_visible=True))
