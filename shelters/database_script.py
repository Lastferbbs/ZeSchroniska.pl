#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import django

import sys


sys.path.append("/home/bsc-node/sol_exp/Zeschroniska.pl/zeschroniska")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zeschroniska.settings")
django.setup()
from shelters.models import Animal, Shelter
import shelters.scrapers.scaper_otozschroniskozg as otoz
import shelters.scrapers.scraper_schroniskodg as schroniskodg
import shelters.scrapers.scraper_schroniskowroclaw as schroniskowroclaw

# shelters = [
#     {schroniskodg.SchroniskoDG():,
#     otoz.OtozSchroniskoZg(),
#     schroniskowroclaw.SchroniskoWro(),
# ]
shelters = {
    otoz.OtozSchroniskoZg(): otoz.AnimalOtoz,
    schroniskodg.SchroniskoDG(): schroniskodg.AnimalDG,
    schroniskowroclaw.SchroniskoWro(): schroniskowroclaw.AnimalWro,
}
# TODO: zebrać wszystkie klasy schronisk w jednym pliku, załadować je,
# wywołać funkcję get_all_dogs_from_website() i porównać z bazą danych
# dodać nowe wpisy do bazy danych, usunąć nieaktualne lub je oznaczyć jako nieaktualne

# TODO: zrobić to samo dla kotów

# TODO: przejrzeć metody w klasach i usunąć nieużywane

listings_in_db = set()
for dog in Animal.objects.all():
    listings_in_db.add(dog.link)


for shelter, animal_class in shelters.items():
    listings_in_db_dogs = set()
    listings_in_db_cats = set()

    if Shelter.objects.filter(name=shelter.name).exists():
        shel = Shelter.objects.get(name=shelter.name)
        for dog in Animal.objects.filter(shelter=shel, animal_type="dog"):
            listings_in_db.add(dog.link)
        for cat in Animal.objects.filter(shelter=shel, animal_type="cat"):
            listings_in_db_cats.add(cat.link)
    else:
        shel = Shelter(
            name=shelter.get_name(),
            address=shelter.get_address(),
            city=shelter.get_city(),
            phone=shelter.get_phone(),
            email=shelter.get_email(),
            website=shelter.get_website(),
        )

        shel.save()

    dogs_from_website = shelter.get_all_dogs_from_website()
    not_active_dogs = listings_in_db - dogs_from_website
    new_dogs = dogs_from_website - listings_in_db

    cats_from_website = shelter.get_all_cats_from_website()
    not_active_cats = listings_in_db - cats_from_website
    new_cats = cats_from_website - listings_in_db

    for dog in new_dogs:
        dog = animal_class(dog, "dog", shelter)
        dog.download_animal_link_content()
        dog.set_animal_details()
        dog.set_animal_pictures()
        ani = Animal(
            name=dog.get_name(),
            age=dog.get_age(),
            age_in_months=dog.get_age_in_months(),
            sex=dog.get_sex(),
            breed=dog.get_breed(),
            description=dog.get_description(),
            pictures=",".join(dog.get_pictures()),
            shelter=shel,
            publication_date=dog.get_publication_date(),
            size=dog.get_size(),
            link=dog.get_link(),
            animal_type=dog.get_animal_type(),
            in_shelter_from=dog.get_in_shelter_from(),
            sterilized=dog.get_sterilized(),
        )
        ani.save()
    for dog in not_active_dogs:
        ani = Animal.objects.get(link=dog)
        ani.valid = False
        ani.save()

    for cat in new_cats:
        cat = animal_class(cat, "cat", shelter)
        cat.download_animal_link_content()
        cat.set_animal_details()
        cat.set_animal_pictures()
        ani = Animal(
            name=cat.get_name(),
            age=cat.get_age(),
            age_in_months=cat.get_age_in_months(),
            sex=cat.get_sex(),
            breed=cat.get_breed(),
            description=cat.get_description(),
            pictures=",".join(cat.get_pictures()),
            shelter=shel,
            publication_date=cat.get_publication_date(),
            size=cat.get_size(),
            link=cat.get_link(),
            animal_type=cat.get_animal_type(),
            in_shelter_from=cat.get_in_shelter_from(),
            sterilized=cat.get_sterilized(),
        )
        ani.save()
    for cat in not_active_cats:
        ani = Animal.objects.get(link=cat)
        ani.valid = False
        ani.save()

# for dog in Animal.objects.all():
#     listings_in_db.add(dog.link)

# for shelter in Shelter.objects.all():
#     pass


# schronisko = otoz.OtozSchroniskoZg()
# dogs_from_website = schronisko.get_all_dogs_from_website()

# nieaktualne = dogs_from_website - listings_in_db
# nowe = listings_in_db - dogs_from_website
# for nowy in nowe:
#     dog = otoz.DogOtoz(nowy, "pies", schronisko)

#     dog.download_dog_link_content()
#     dog.set_dog_details()
#     # dog.set_dog_pictures()
#     dog.print_dog_details()
