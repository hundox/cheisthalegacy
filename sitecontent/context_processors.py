from .data import CONTACTS
from .models import ContactDetail, NavigationItem, PageSection, SiteConfiguration


def site_globals(request):
    sections = {f"{item.page.slug}.{item.key}": item for item in PageSection.objects.filter(is_visible=True).select_related("page")}
    nav = list(NavigationItem.objects.filter(is_visible=True, parent__isnull=True).prefetch_related("children"))
    for item in nav:
        item.visible_children = list(item.children.filter(is_visible=True))
    contacts = list(ContactDetail.objects.filter(is_visible=True)) or CONTACTS
    config = SiteConfiguration.objects.first()
    return {"contacts": contacts, "navigation_items": nav, "site_sections": sections, "site_config": config}
