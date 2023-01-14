# sys.path.append("..")
from django.shortcuts import render
from .models import Animal, Shelter
from .consts import SHELTERS_CITIES

# from .scrapers import scaper_otozschroniskozg
from django.core import serializers
from django.core.paginator import (
    Paginator,
)
from django.contrib import messages
from django.views.generic import ListView, DetailView, TemplateView, FormView

from django.core.mail import send_mail
from django.forms import ModelForm
from django.template.loader import render_to_string

from .forms import ContactPageForm

from .filters import AnimalFilter
from .api import API_KEY

import requests


link = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins=placeholder&destinations={'|'.join(SHELTERS_CITIES)}&units=imperial&key={API_KEY}&language=pl"

# Create your views here.


class HomePageView(TemplateView):
    template_name = "shelters/home.html"


class SheltersPageView(TemplateView):
    template_name = "shelters/schroniska.html"


# class ContactPageForm(ModelForm):
#     class Meta:
#         model = Animal
#         fields = ["name", "age", "breed


class ContactPageView(FormView):
    template_name = "shelters/contact.html"
    form_class = ContactPageForm
    success_url = "/contact/"
    redirect = "/contact/"
    form = ContactPageForm()

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, "Wiadomość została wysłana")
        return super().form_valid(form)


class AnimalDetailView(DetailView):
    model = Animal
    context_object_name = "animal"
    template_name = "shelters/animal_card.html"


def dogs(request, cats=False):
    animal = "dog"
    if cats:
        animal = "cat"

    current_filters = current_filters_helper(request.get_full_path())
    animal_filter = AnimalFilter(
        request.GET, queryset=Animal.objects.filter(animal_type=animal)
    )
    excluded_cities_filter, query_set = distance_api_helper(
        animal_filter.qs,
        request.GET.get("distance"),
        request.GET.get("city"),
        request.GET.get("excluded_cities"),
    )
    paginator = Paginator(query_set, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "shelters/dogs.html",
        {
            "dogs_json": page_obj,
            "filters": animal_filter,
            "current_filters": current_filters,
            "excluded_cities": excluded_cities_filter,
        },
    )


def cats(request):

    return dogs(request, cats=True)


# TODO simple way to get current filters from url, move to separate file, maybe merge with excluded_cities
def current_filters_helper(url):
    current_filters_list = []
    current_filters = url.split("?")
    if len(current_filters) > 1:
        current_filters = current_filters[1].split("&")
        for c_filter in current_filters:
            if "page" not in c_filter and "excluded_cities" not in c_filter:
                current_filters_list.append(c_filter)

        current_filters = "&".join(current_filters_list)
        if current_filters:
            current_filters = "&" + current_filters
    else:
        current_filters = ""

    return current_filters


# we could optimize this by memoizing the distance between cities
def distance_api_helper(query_set, distance, city, excluded_cities):
    if distance and city:

        if excluded_cities:
            excluded_cities = excluded_cities.split("|")
            for excluded_city in excluded_cities:
                query_set = query_set.exclude(shelter__city=excluded_city)
            excluded_cities_filter = "&excluded_cities=" + "|".join(excluded_cities)
        else:
            excluded_cities_filter = "&excluded_cities="
            response = requests.get(link.replace("placeholder", city + "+pl"))
            response = response.json()
            print(response)
            for index, element in enumerate(response["rows"][0]["elements"]):
                if element["status"] == "OK":
                    # print((element["distance"]["value"], int(distance) * 1000))
                    if (element["distance"]["value"]) > int(distance) * 1000:
                        query_set = query_set.exclude(
                            shelter__city=SHELTERS_CITIES[index]
                        )
                        excluded_cities_filter += SHELTERS_CITIES[index] + "|"
                        # print(query_set)
        return excluded_cities_filter, query_set
    return "", query_set
