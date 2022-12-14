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
    default_page = 1
    page = request.GET.get("page", default_page)
    all_dogs = Animal.objects.all()
    paginator = Paginator(all_dogs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "shelters/dogs.html",
        {"dogs_json": page_obj},
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
