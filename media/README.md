# Uploads

Upload original website photographs and videos through Django Admin. Files are stored under `media/site/media/` (the `MediaAsset` upload path) and served from `/media/` in local development. For production, persist this directory or configure object storage before enabling uploads.

The media binaries are stored in `media/site/media/`. After adding or replacing files there, run `python manage.py sync_local_media` to connect matching filenames to their seeded page slots. Any still-missing file can be uploaded on its matching row in **Admin → Media assets**; the existing filename mapping places it in the right slot.
