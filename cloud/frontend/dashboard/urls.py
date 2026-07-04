from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("tenants/", views.tenants_view, name="tenants"),
]
