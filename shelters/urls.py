from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="shelters/index"),
    path("home/", views.home, name="shelters/home"),
    path("all_items_test/", views.all_items_test, name="shelters/all_items_test"),
    path("dogs/", views.dogs, name="shelters/dogs"),
    path("dogs/<int:dog_id>/", views.dog, name="shelters/dog"),
    path("dogs_test/", views.dogs_test, name="shelters/dogs_test"),
]
