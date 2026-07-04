from django.urls import path

from . import views

urlpatterns = [
    path("collectors/register", views.register_collector_view, name="register_collector"),
    path("collectors/<str:collector_id>/ingest", views.ingest_view, name="ingest"),
]
