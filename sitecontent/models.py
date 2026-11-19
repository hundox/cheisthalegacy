from django.core.validators import FileExtensionValidator
from django.db import models


class SitePage(models.Model):
    slug = models.SlugField(unique=True, help_text="Stable key used by page sections, e.g. home or foundation.")
    title = models.CharField(max_length=180)
    meta_description = models.CharField(max_length=320, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ("slug",)

    def __str__(self):
        return self.title


class SiteConfiguration(models.Model):
    name = models.CharField(max_length=80, default="Main configuration", unique=True)
    site_name = models.CharField(max_length=180, default="The Cheistha Kochhar Foundation")
    linkedin_url = models.URLField(blank=True, default="https://in.linkedin.com/company/cheistha-kochhar-foundation")
    partnership_url = models.URLField(blank=True, default="https://docs.google.com/forms/d/e/1FAIpQLSdqSK-5Hza3rsq9cASGmVS9-aDtL3eCBaS2mEUBdxrQkRdxyw/viewform?usp=publish-editor")
    forever_missed_url = models.URLField(blank=True, default="https://www.forevermissed.com/cheistha-kochhar/stories")

    def __str__(self):
        return self.name


class PageSection(models.Model):
    page = models.ForeignKey(SitePage, on_delete=models.CASCADE, related_name="sections")
    key = models.SlugField(help_text="Unique key within this page; templates use it to display this block.")
    eyebrow = models.CharField(max_length=140, blank=True)
    heading = models.CharField(max_length=240, blank=True)
    body = models.TextField(blank=True, help_text="Plain text. Separate paragraphs with a blank line.")
    image = models.ImageField(upload_to="site/sections/", blank=True, validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp", "gif"])])
    image_alt = models.CharField(max_length=240, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ("page__slug", "order", "id")
        constraints = [models.UniqueConstraint(fields=("page", "key"), name="unique_page_section_key")]

    def __str__(self):
        return f"{self.page.slug}: {self.heading or self.key}"


class NavigationItem(models.Model):
    label = models.CharField(max_length=100)
    url = models.CharField(max_length=300, help_text="Internal path or full external URL.")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    open_in_new_tab = models.BooleanField(default=False)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.label


class Chapter(models.Model):
    JOURNEY = "journey"
    PROFESSIONAL = "professional"
    KIND_CHOICES = [(JOURNEY, "Remembering Cheistha: formative years"), (PROFESSIONAL, "Professional journey")]
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=180)
    period = models.CharField(max_length=120, blank=True)
    tagline = models.CharField(max_length=300, blank=True)
    intro = models.TextField(blank=True, help_text="Separate paragraphs with a blank line.")
    highlights = models.TextField(blank=True, help_text="One highlight per line.")
    institution = models.CharField(max_length=250, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ("kind", "order", "id")

    def __str__(self):
        return self.title

    @property
    def intro_paragraphs(self):
        return [p.strip() for p in self.intro.split("\n\n") if p.strip()]

    @property
    def highlight_items(self):
        return [line.strip() for line in self.highlights.splitlines() if line.strip()]

    @property
    def type(self):
        return self.kind


class Initiative(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=220)
    institution = models.CharField(max_length=300)
    tagline = models.CharField(max_length=320)
    description = models.TextField(help_text="Separate paragraphs with a blank line.")
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.title

    @property
    def description_paragraphs(self):
        return [p.strip() for p in self.description.split("\n\n") if p.strip()]


class FocusArea(models.Model):
    title = models.CharField(max_length=180)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.title


class ContactDetail(models.Model):
    name = models.CharField(max_length=160)
    role = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.name} ({self.role})"


class MediaAsset(models.Model):
    ROLE_CHOICES = [
        ("site", "Site-wide brand / interface"), ("hero", "Page hero"), ("portrait", "Portrait"),
        ("chapter_cover", "Chapter cover"), ("chapter_identity", "Organisation / campus identity"),
        ("chapter_gallery", "Chapter gallery photo"), ("initiative_primary", "Initiative primary image"),
        ("initiative_satellite", "Initiative gallery satellite"), ("quote", "Quotation slide"), ("other", "Other"),
    ]
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="site/media/", blank=True, validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp", "gif", "mp4", "webm"])])
    alt_text = models.CharField(max_length=300, blank=True)
    role = models.CharField(max_length=24, choices=ROLE_CHOICES, default="other")
    legacy_filename = models.CharField(max_length=180, blank=True, unique=True, help_text="Matching original filename; uploading it restores this media slot.")
    page = models.ForeignKey(SitePage, null=True, blank=True, on_delete=models.CASCADE, related_name="media")
    chapter = models.ForeignKey(Chapter, null=True, blank=True, on_delete=models.CASCADE, related_name="media")
    initiative = models.ForeignKey(Initiative, null=True, blank=True, on_delete=models.CASCADE, related_name="media")
    collection_key = models.SlugField(blank=True, help_text="Optional photo-set key used to separate merged initiative galleries.")
    slot = models.PositiveIntegerField(default=0, help_text="Satellite position is zero-based: 0 top-left, 1 top-right, 2 bottom-left, 3 bottom-right.")
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "slot", "id")

    def __str__(self):
        return self.title

    @property
    def url(self):
        return self.file.url if self.file else ""

    @property
    def kind(self):
        name = self.file.name.lower()
        return "video" if name.endswith((".mp4", ".webm")) else "image"
