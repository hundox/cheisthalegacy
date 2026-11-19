from pathlib import Path
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from sitecontent.models import Chapter, MediaAsset, SitePage


class Command(BaseCommand):
    help = "Link files already in media/site/media to their seeded website media slots."

    # The image is present locally as PNG, while the source site's descriptor used JPG.
    FILE_ALIASES = {"brics-cci-woman-icon.jpg": "brics-cci-woman-icon.png"}

    def handle(self, *args, **options):
        media_dir = Path(settings.MEDIA_ROOT) / "site" / "media"
        if not media_dir.is_dir():
            self.stderr.write(self.style.ERROR(f"Media folder not found: {media_dir}"))
            return

        home_page = SitePage.objects.filter(slug="home").first()
        manifest_path = Path(settings.BASE_DIR) / "sitecontent" / "legacy_media.json"
        media_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        chapter_by_filename = {}
        for chapter_slug, photos in media_manifest.get("chapters", {}).items():
            for order, photo in enumerate(photos):
                chapter_by_filename[photo["filename"]] = (chapter_slug, order)

        attached = 0
        already_linked = 0
        missing = []

        for asset in MediaAsset.objects.exclude(legacy_filename="").order_by("legacy_filename"):
            chapter_placement = chapter_by_filename.get(asset.legacy_filename)
            if chapter_placement:
                chapter_slug, photo_order = chapter_placement
                updates = []
                target_chapter = Chapter.objects.filter(slug=chapter_slug).first()
                if target_chapter and asset.chapter_id != target_chapter.id:
                    asset.chapter = target_chapter
                    updates.append("chapter")
                if asset.role != "chapter_gallery":
                    asset.role = "chapter_gallery"
                    updates.append("role")
                if asset.order != photo_order:
                    asset.order = photo_order
                    updates.append("order")
                if updates:
                    asset.save(update_fields=updates)

            # Set the slideshow classification even when one source image is missing locally.
            if asset.legacy_filename.startswith("cheistha-quote-") and home_page:
                updates = []
                if asset.role != "quote":
                    asset.role = "quote"
                    updates.append("role")
                if asset.page_id != home_page.id:
                    asset.page = home_page
                    updates.append("page")
                if updates:
                    asset.save(update_fields=updates)

            actual_name = self.FILE_ALIASES.get(asset.legacy_filename, asset.legacy_filename)
            disk_file = media_dir / actual_name
            if not disk_file.is_file():
                missing.append(asset.legacy_filename)
                continue

            relative_name = f"site/media/{actual_name}"
            changed = asset.file.name != relative_name
            if changed:
                asset.file.name = relative_name
                asset.save(update_fields=["file"])
                attached += 1
            else:
                already_linked += 1

        self.stdout.write(self.style.SUCCESS(
            f"Linked {attached} files; {already_linked} were already linked; "
            f"{len(missing)} referenced files are absent."
        ))
        if missing:
            self.stdout.write("Missing filenames:")
            for name in missing:
                self.stdout.write(f"  - {name}")
