from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html

from .models import (
    Chapter,
    ContactDetail,
    FocusArea,
    Initiative,
    MediaAsset,
    NavigationItem,
    PageSection,
    SiteConfiguration,
    SitePage,
)


admin.site.site_header = "Cheistha Kochhar Foundation"
admin.site.site_title = "Foundation Admin"
admin.site.index_title = "Manage website content"


class PageSectionInline(admin.StackedInline):
    model = PageSection
    extra = 0
    classes = ("collapse",)
    fields = ("order", "key", "eyebrow", "heading", "body", "image", "image_alt", "is_visible")
    ordering = ("order",)


class NavigationChildInline(admin.TabularInline):
    model = NavigationItem
    fk_name = "parent"
    extra = 0
    fields = ("label", "url", "order", "is_visible")
    ordering = ("order",)


class UploadStateFilter(SimpleListFilter):
    title = "upload status"
    parameter_name = "uploaded"

    def lookups(self, request, model_admin):
        return (("yes", "Uploaded"), ("no", "Missing file"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(file="")
        if self.value() == "no":
            return queryset.filter(file="")
        return queryset


@admin.register(SitePage)
class SitePageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "slug")
    inlines = (PageSectionInline,)
    fieldsets = (("Page", {"fields": ("title", "slug", "is_published", "meta_description")}),)


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ("heading", "page", "key", "order", "is_visible")
    list_filter = ("page", "is_visible")
    search_fields = ("heading", "eyebrow", "body", "key")
    list_editable = ("order", "is_visible")
    fields = ("page", "key", "eyebrow", "heading", "body", "image", "image_alt", "order", "is_visible")


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ("label", "url", "parent", "order", "is_visible")
    list_filter = ("is_visible", "parent")
    search_fields = ("label", "url")
    list_editable = ("order", "is_visible")
    inlines = (NavigationChildInline,)
    fields = ("label", "url", "parent", "order", "is_visible", "open_in_new_tab")


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "period", "order", "is_published")
    list_filter = ("kind", "is_published")
    search_fields = ("title", "slug", "period", "tagline", "institution")
    list_editable = ("order", "is_published")
    fieldsets = (
        ("Chapter", {"fields": ("kind", "title", "slug", "period", "tagline", "institution", "order", "is_published")}),
        ("Page text", {"fields": ("intro", "highlights"), "classes": ("collapse",)}),
    )


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ("title", "institution", "order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "slug", "institution", "tagline", "description")
    list_editable = ("order", "is_published")
    fields = ("title", "slug", "institution", "tagline", "description", "order", "is_published")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "upload_status", "role", "destination", "legacy_filename")
    list_filter = (UploadStateFilter, "role", "is_visible")
    search_fields = ("title", "alt_text", "legacy_filename", "file")
    list_per_page = 30
    fieldsets = (
        ("Choose the file", {"fields": ("title", "file", "alt_text")}),
        ("Where it appears", {"fields": ("role", "page", "chapter", "initiative", "collection_key", "slot", "order", "is_visible")}),
        ("Filename mapping", {"fields": ("legacy_filename",)}),
    )

    @admin.display(description="File")
    def upload_status(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank" rel="noopener">View uploaded file</a>', obj.file.url)
        return "Missing"

    @admin.display(description="Used on")
    def destination(self, obj):
        return obj.chapter or obj.initiative or obj.page or "Shared media"


@admin.register(FocusArea)
class FocusAreaAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_visible")
    list_editable = ("order", "is_visible")
    search_fields = ("title", "description")
    fields = ("title", "description", "order", "is_visible")


@admin.register(ContactDetail)
class ContactDetailAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "email", "phone", "is_visible")
    list_editable = ("is_visible",)
    search_fields = ("name", "role", "email", "phone")
    fields = ("name", "role", "email", "phone", "order", "is_visible")


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ("name", "site_name")
    fields = ("name", "site_name", "linkedin_url", "partnership_url", "forever_missed_url")
