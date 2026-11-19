# The Cheistha Kochhar Foundation

This repository now contains a Django implementation of the Foundation archive. The website is server-rendered using Django templates, with responsive styling in `static/site/site.css` and a small JavaScript file for the mobile navigation.

## Run locally

Requires Python 3.10 or newer.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_site_content
python manage.py sync_local_media
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/> for the site or <http://127.0.0.1:8000/admin/> to log in with the superuser you created. On an existing install, rerun `sync_local_media` after copying in media files; it does not overwrite page content.

## Manage the website in Django Admin

- **Site pages** contain editable page titles, search descriptions, publish toggles, and inline page sections. Page sections hold eyebrow labels, headings, text, and optional uploaded images.
- **Navigation items** control every top-level link and the Remembering Cheistha submenu. Set a parent on submenu links and adjust order/visibility.
- **Chapters** edit the four formative-year pages and eight professional chapters, including their copy, highlights, order, and publishing state.
- **Initiatives** edit the Foundation's Legacy in Action cards and detail pages. Focus areas and contact details have their own Admin sections.
- **Media assets** contains rows for the image/video names the original site referenced. Existing files in `media/site/media/` can be linked to those slots with `python manage.py sync_local_media`; new uploads can be added from Admin. Initiative satellite slots use 0 top-left, 1 top-right, 2 bottom-left, and 3 bottom-right. For the two combined initiative galleries, set the collection key to `people-speak-memorial-debate` or `jibs-nudge-lab-rolling-trophy` to keep the event sets separate.
- **Site configuration** controls the LinkedIn, partnership form, and ForeverMissed links.

## Deployment

### Vercel

Import this repository into Vercel as a Django project. Vercel detects `manage.py` and runs `collectstatic` during the build. Create a persistent PostgreSQL database and set these environment variables for each Vercel environment:

- `DATABASE_URL`: the PostgreSQL connection URL, including any provider-required SSL options.
- `DJANGO_SECRET_KEY`: a long, random secret.
- `DJANGO_DEBUG`: `false`.
- `DJANGO_ALLOWED_HOSTS`: comma-separated custom domains, if any. Vercel's `*.vercel.app` hosts are already allowed.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: comma-separated HTTPS origins for any custom domains used to access the admin, for example `https://example.com`.

Before serving traffic, initialize the new database from a trusted local terminal with the same `DATABASE_URL` set. Install the requirements, then run:

```sh
python manage.py migrate
python manage.py loaddata sitecontent/initial_content.json
python manage.py createsuperuser
```

The fixture captures the existing site content without user accounts. Load it only into a new, empty database; it can overwrite records on an existing site. Subsequent content edits live in PostgreSQL. Local SQLite and Vercel's temporary filesystem are not persistent production databases.

The checked-in media is collected as static files and served from Vercel's CDN. Vercel's filesystem is read-only at runtime, so uploads through Django Admin require a separately configured persistent object-storage backend; editing text and selecting existing media records does not require uploads. To add bundled media, commit the files and redeploy. Provision external storage before relying on Admin uploads.

For a conventional server, set `DJANGO_DEBUG=false`, `DJANGO_SECRET_KEY` to a long random secret, and `DJANGO_ALLOWED_HOSTS` to the deployed hostname(s). Then run:

```sh
python manage.py collectstatic --noinput
gunicorn foundation_site.wsgi:application
```

WhiteNoise serves the collected static files. Use a managed database only if content is later moved from the code-defined archive into Django models.

## Media assets

The media files are stored in `media/site/media/`. To map them to their seeded page slots, run `python manage.py sync_local_media`. The command links files by filename and reports any referenced files that are still absent. In the current folder, these 11 files are missing: `aps-mhow-cheistha-newspaper.jpeg`, `cheistha-end-frame.png`, `cheistha-portrait.jpeg`, `cheistha-quote-020.jpg`, `chicago-shield.webp`, `good-samaritan-Screenshot_2026-10-05_121555.png`, `good-samaritan-Screenshot_2026-10-05_121614.png`, `lse-logo.png`, `memorial-lecture-Screenshot_2026-10-05_120521.png`, `nudge-awards-certificate.png`, and `nudge-awards-primary.png`. When you obtain one, upload it to its row in **Admin → Media assets**.

The Admin creates a superuser account but does not choose credentials for you. For an existing local checkout, run `python manage.py createsuperuser` once, then sign in at `/admin/`. After the first seed, rerunning `python manage.py seed_site_content` adds missing archive records without overwriting content you have edited.
