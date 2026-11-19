from django.core.management.base import BaseCommand
from sitecontent.data import CHAPTERS, CONTACTS, FOCUS_AREAS, INITIATIVES
import json
from pathlib import Path
from django.conf import settings
from sitecontent.models import Chapter, ContactDetail, FocusArea, Initiative, MediaAsset, NavigationItem, PageSection, SiteConfiguration, SitePage


class Command(BaseCommand):
    help = "Load the original site content into editable Django Admin records. Existing records are left as edited."

    def handle(self, *args, **options):
        pages = {
            "home": "The Cheistha Kochhar Foundation | In Loving Memory",
            "foundation": "The Foundation | The Cheistha Kochhar Foundation",
            "initiatives": "Legacy in Action | The Cheistha Kochhar Foundation",
            "journey": "Remembering Cheistha | The Cheistha Kochhar Foundation",
            "professional": "Professional Journey | The Cheistha Kochhar Foundation",
            "gallery": "Gallery | The Cheistha Kochhar Foundation",
            "timeline": "Timeline | The Cheistha Kochhar Foundation",
            "search": "Search | The Cheistha Kochhar Foundation",
            "contact": "Foundation Information | The Cheistha Kochhar Foundation",
        }
        for slug, title in pages.items():
            SitePage.objects.get_or_create(slug=slug, defaults={"title": title})

        sections = [
            ("home", "hero", "In loving memory of Cheistha Kochhar", "The Cheistha Kochhar Foundation", "Advancing Nudge theory, research, education and public policy, translating thoughtful ideas into lasting social impact, in partnership with universities, public institutions and global organisations."),
            ("home", "foundation", "The Foundation", "What the Foundation does", "The Cheistha Kochhar Foundation carries forward her conviction that rigorous ideas, applied with empathy, can change how institutions serve people through nudge theory, public policy, education and scholarships, leadership programmes, memorial lectures and partnerships. Its continuing work is gathered under Legacy in Action."),
            ("home", "remembering", "The person behind the Foundation", "Remembering Cheistha", "Behind every initiative is a person whose ideas, values and cheerful courage made this work possible. What follows is her story: a curious mind shaped by school corridors, university halls and a lifelong belief in public service."),
            ("home", "journey", "Her life & education", "Her Formative Years", "Four chapters, a clockwise walk around her portrait, trace a curious, cheerful mind through childhood, primary school, senior school and college."),
            ("home", "professional", "Her work & institutions", "Professional Journey", "This chapter explores Cheistha Kochhar's professional experiences and the institutions that shaped her career and public service journey."),
            ("foundation", "overview", "Foundation Overview", "The Cheistha Kochhar Foundation", "The Cheistha Kochhar Foundation carries forward the legacy of Cheistha Kochhar, a brilliant economist, researcher, policy professional and behavioural strategist whose life embodied intellect, empathy and an unwavering commitment to national and social good."),
            ("foundation", "recognition", "Recognition and continuing remembrance", "Recognition and continuing remembrance", "A recipient of numerous honours including the LSE Research Fellowship, Young India Fellowship, Clinton Global Fellowship (2019), Erwin B. Harris Scholarship, Roshan Lal Trust Scholarship and the Tata Scholarship, her achievements reflected her exceptional promise. Though her life was tragically cut short in an accident, her impact continues to grow. The London School of Economics now confers the Cheistha Kochhar Master of Research Prize on her birthday and has named its PhD study room after her. The University of Delhi hosts an annual memorial lecture and rolling trophies for the Best Nudge Project. ISPP and the Harris School of Public Policy, University of Chicago, have renamed the Anubhav Series in her honour and established multiple scholarships. Sri Venkateswara College, Army Public School Mhow, Ashoka University, MANAS School and C-DEP also commemorate her through annual lectures, awards and scholarships. Her personal library has been shared with Ashoka University and the Military College of Telecommunications."),
            ("foundation", "purpose", "The Foundation's purpose", "The Foundation's purpose", "Founded in her memory, the Foundation advances her vision through initiatives in education, gender equity, behavioural science, social impact research, community and animal welfare, and organisational behaviour. Guided by her pioneering work, we strive to build an inclusive, equitable and compassionate world through collaborations, scholarships, research and meaningful dialogue."),
            ("foundation", "legacy-in-action", "The Foundation's work", "Legacy in Action", "Cheistha's vision continues to inspire a growing movement across academia, public policy, behavioural science and social impact. Through collaborations with leading universities, public institutions and global organisations, the Foundation advances her commitment to behavioural science, research, leadership and public service."),
            ("foundation", "focus", "Our areas of work", "What we carry forward", "The Foundation's focus areas and programmes."),
            ("contact", "hero", "Foundation Information", "In touch with the Foundation", "The Cheistha Kochhar Foundation exists to preserve her memory and carry her spirit forward. Below are the ways to learn more, follow along, and contribute to this living archive."),
        ]
        for order, (page_slug, key, eyebrow, heading, body) in enumerate(sections):
            PageSection.objects.get_or_create(page__slug=page_slug, key=key, defaults={
                "page": SitePage.objects.get(slug=page_slug), "eyebrow": eyebrow, "heading": heading, "body": body, "order": order,
            })

        menu = [
            ("Home", "/", None), ("Foundation", "/foundation", None),
            ("Legacy in Action", "/foundation#legacy-in-action", None),
            ("Remembering Cheistha", "/#remembering", [
                ("Her Formative Years", "/#journey"), ("Professional Journey", "/professional"),
                ("Gallery", "/gallery"), ("Timeline", "/timeline"), ("Search", "/search"),
            ]),
            ("Contact", "/contact", None),
        ]
        for order, (label, url, children) in enumerate(menu):
            parent, _ = NavigationItem.objects.get_or_create(parent=None, label=label, defaults={"url": url, "order": order})
            if children:
                for child_order, (child_label, child_url) in enumerate(children):
                    NavigationItem.objects.get_or_create(parent=parent, label=child_label, defaults={"url": child_url, "order": child_order})

        for order, item in enumerate(CHAPTERS):
            Chapter.objects.get_or_create(slug=item["slug"], defaults={
                "kind": item["type"], "title": item["title"], "period": item.get("period", ""),
                "tagline": item.get("tagline", ""), "intro": "\n\n".join(item.get("intro", [])),
                "highlights": "\n".join(item.get("highlights", [])), "order": order,
            })
        for order, item in enumerate(INITIATIVES):
            Initiative.objects.get_or_create(slug=item["slug"], defaults={
                "title": item["title"], "institution": item["institution"], "tagline": item["tagline"],
                "description": item["description"], "order": order,
            })
        for order, (title, description) in enumerate(FOCUS_AREAS):
            FocusArea.objects.get_or_create(title=title, defaults={"description": description, "order": order})
        for order, item in enumerate(CONTACTS):
            ContactDetail.objects.get_or_create(email=item["email"], defaults={**item, "order": order})

        SiteConfiguration.objects.get_or_create(name="Main configuration")
        chapters_by_slug = {item.slug: item for item in Chapter.objects.all()}
        initiatives_by_slug = {item.slug: item for item in Initiative.objects.all()}
        asset_manifest = json.loads((Path(settings.BASE_DIR) / "sitecontent" / "legacy_media.json").read_text(encoding="utf-8"))
        url_map = json.loads((Path(settings.BASE_DIR) / "sitecontent" / "legacy_asset_urls.json").read_text(encoding="utf-8"))
        placements = {}
        for slug, photos in asset_manifest["chapters"].items():
            for photo_order, photo in enumerate(photos):
                placements[photo["filename"]] = {
                    "chapter": chapters_by_slug.get(slug), "role": "chapter_gallery",
                    "alt_text": photo["alt"], "order": photo_order,
                }
        for slug, photo in asset_manifest["primary"].items():
            main_slug = {"people-speak-memorial-debate": "annual-memorial-lecture-svc", "jibs-nudge-lab-rolling-trophy": "jibs-strategic-partnership"}.get(slug, slug)
            placements[photo["filename"]] = {"initiative": initiatives_by_slug.get(main_slug), "collection_key": slug, "role": "initiative_primary", "alt_text": photo["alt"]}
        for slug, photos in asset_manifest["satellites"].items():
            main_slug = {"people-speak-memorial-debate": "annual-memorial-lecture-svc", "jibs-nudge-lab-rolling-trophy": "jibs-strategic-partnership"}.get(slug, slug)
            for slot, photo in enumerate(photos):
                placements[photo["filename"]] = {"initiative": initiatives_by_slug.get(main_slug), "collection_key": slug, "role": "initiative_satellite", "slot": slot, "alt_text": photo["alt"]}
        for filename in url_map:
            role = "other"
            page = None
            if filename == "foundation-logo.png":
                role, page = "site", SitePage.objects.get(slug="home")
            elif filename == "cheistha-hero.mp4":
                role, page = "hero", SitePage.objects.get(slug="home")
            elif filename in ("cheistha-portrait.jpeg", "hero-portrait.jpg", "glass_card.jpg"):
                role, page = "portrait", SitePage.objects.get(slug="home" if filename != "hero-portrait.jpg" else "foundation")
            elif filename == "professional-cover.jpg":
                role, page = "chapter_cover", SitePage.objects.get(slug="professional")
            elif filename.startswith("image-") and filename.endswith(".jpg"):
                role, page = "quote", SitePage.objects.get(slug="home")
            entry = {"title": filename, "legacy_filename": filename, "role": role, "page": page}
            entry.update(placements.get(filename, {}))
            asset, created = MediaAsset.objects.get_or_create(legacy_filename=filename, defaults=entry)
            if not created and not asset.file:
                for field in ("title", "role", "alt_text", "page", "chapter", "initiative", "collection_key", "slot"):
                    if field in entry:
                        setattr(asset, field, entry[field])
                asset.save()
        self.stdout.write(self.style.SUCCESS("Site pages, sections, menu, chapters, initiatives, focus areas and contacts are ready in Django Admin."))
