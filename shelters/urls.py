from django.urls import path, re_path
from .views import HomePageView, AnimalDetailView

from . import views

urlpatterns = [
    path("", HomePageView.as_view()),
    path("home/", HomePageView.as_view()),
    path("dogs/", views.dogs, name="shelters/dogs"),
    # re_path(r"^dogs/$", views.dogs, name="shelters/dogs"),
    path("animal/<int:pk>/", AnimalDetailView.as_view()),
    path("dogs/<int:pk>/", AnimalDetailView.as_view()),
    path("cats/", views.cats, name="shelters/cats"),
    path("cats/<int:pk>/", AnimalDetailView.as_view()),
    path("contact/", views.ContactPageView.as_view()),
]
