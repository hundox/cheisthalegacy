from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("foundation", views.foundation, name="foundation"),
    path("initiatives", views.initiatives, name="initiatives"),
    path("initiatives/<slug:slug>", views.initiative_detail, name="initiative_detail"),
    path("journey/<slug:slug>", views.journey_detail, name="journey_detail"),
    path("professional", views.professional, name="professional"),
    path("professional/<slug:slug>", views.professional_detail, name="professional_detail"),
    path("gallery", views.gallery, name="gallery"),
    path("gallery/<slug:slug>", views.gallery_detail, name="gallery_detail"),
    path("timeline", views.timeline, name="timeline"),
    path("search", views.search, name="search"),
    path("contact", views.contact, name="contact"),
]
