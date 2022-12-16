# sys.path.append("..")
import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Animal, Shelter

# from .scrapers import scaper_otozschroniskozg
from django.core import serializers
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger,
)
from .filters import AnimalFilter
from .api import API_KEY

import requests

SHELTERS_CITIES = [
    "ul. Ślazowa 2, 51-007 Wrocław",
    "Zielona Góra",
    "Dłużyna Górna 1F, 59-930 Pieńsk",
]
# Create your views here.


def index(request):
    return render(request, "shelters/base.html")


def home(request):

    default_page = 1
    page = request.GET.get("page", default_page)

    # Get queryset of items to paginate
    all_dogs = Animal.objects.all()
    # dogs = serializers.serialize("json", all_dogs)
    # dogs_json = json.loads(dogs)
    # for dog in dogs_json:
    #     dog["fields"]["pictures"] = dog["fields"]["pictures"].split(",")[0]
    # di = {}

    # Paginate items
    items_per_page = 12
    paginator = Paginator(all_dogs, items_per_page)

    items_page = paginator.get_page(page)
    # except PageNotAnInteger:
    #     items_page = paginator.page(default_page)
    # except EmptyPage:
    #     items_page = paginator.page(paginator.num_pages)

    # Provide filtered, paginated library items

    return render(
        request,
        "shelters/home.html",
        {"dogs_json": all_dogs[:5]},
    )


def all_items_test(request):
    all_dogs = Animal.objects.all()
    dogs = serializers.serialize("json", all_dogs)
    dogs_json = json.loads(dogs)
    for dog in dogs_json:
        dog["fields"]["pictures"] = dog["fields"]["pictures"].split(",")[0]
    di = {}
    return render(
        request,
        "shelters/all_items_test.html",
        {"dogs_json": dogs_json},
    )


def dogs(request):

    # Get queryset of items to paginate
    current_filters_list = []
    current_filters = request.build_absolute_uri().split(
        "?"
    )  # TODO simple way to get current filters from url, move to separate file, maybe merge with excluded_cities
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

    all_dogs = Animal.objects.all()
    animal_filter = AnimalFilter(request.GET, queryset=all_dogs)
    distance = request.GET.get("distance")
    city = request.GET.get("city")

    query_set = animal_filter.qs
    # print(animal_filter.qs)
    if (  # TODO Move this to separate file, maybe merge with current_filters
        distance and city
    ):  # we could optimize this by memoizing the distance between cities
        print(request.GET.get("excluded_cities"))
        if request.GET.get("excluded_cities"):

            # print(request.GET.get("excluded_cities").split("&"))
            excluded_cities = request.GET.get("excluded_cities").split("|")
            for excluded_city in excluded_cities:
                if excluded_city:
                    query_set = query_set.exclude(shelter__city=excluded_city)
            excluded_cities = "&excluded_cities=" + "|".join(excluded_cities)
        else:
            excluded_cities = "&excluded_cities="
            response = requests.get(
                f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={city}&destinations={'|'.join(SHELTERS_CITIES)}&units=imperial&key={API_KEY}&language=pl"
            )
            response = response.json()
            print(response)
            for index, element in enumerate(response["rows"][0]["elements"]):
                if element["status"] == "OK":
                    # print((element["distance"]["value"], int(distance) * 1000))
                    if (element["distance"]["value"]) > int(distance) * 1000:
                        query_set = query_set.exclude(
                            shelter__city=SHELTERS_CITIES[index]
                        )
                        excluded_cities += SHELTERS_CITIES[index] + "|"
                        # print(query_set)
    else:
        excluded_cities = ""
        # if int(distance) < 50:
        #     query_set = animal_filter.qs.exclude(
        #         shelter__city="Dłużyna Górna 1F, 59-930 Pieńsk"
        #     )

    # sterylizacja = request.GET.get("sterylizacja")
    # filters = ""
    # if sterylizacja == "1":
    #     filters += "&sterylizacja=" + sterylizacja
    #     all_dogs = Animal.objects.filter(sex="samica")
    paginator = Paginator(query_set, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    # print(excluded_cities)

    return render(
        request,
        "shelters/dogs.html",
        {
            "dogs_json": page_obj,
            "filters": animal_filter,
            "current_filters": current_filters,
            "excluded_cities": excluded_cities,
        },
    )


def dogs_test(request):

    # Get queryset of items to paginate
    all_dogs = Animal.objects.all()
    paginator = Paginator(all_dogs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "shelters/all_items_test.html",
        {"dogs_json": page_obj},
    )


def dog(request, dog_id):  # take care of inactive dogs
    dog = Animal.objects.get(pk=dog_id)
    dog_json = serializers.serialize("json", [dog])
    dog_json = json.loads(dog_json)
    # return JsonResponse(dog_json, safe=False)
    return render(request, "shelters/dog_card.html", {"dog": dog})
