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
    otoz.OtozSchroniskoZg(): otoz.DogOtoz,
    schroniskodg.SchroniskoDG(): schroniskodg.DogDG,
    schroniskowroclaw.SchroniskoWro(): schroniskowroclaw.DogWro,
}
# TODO: zebrać wszystkie klasy schronisk w jednym pliku, załadować je,
# wywołać funkcję get_all_dogs_from_website() i porównać z bazą danych
# dodać nowe wpisy do bazy danych, usunąć nieaktualne lub je oznaczyć jako nieaktualne

# TODO: zrobić to samo dla kotów

# TODO: przejrzeć metody w klasach i usunąć nieużywane

listings_in_db = set()
for dog in Animal.objects.all():
    listings_in_db.add(dog.link)


for shelter, dog_class in shelters.items():
    listings_in_db = set()
    if Shelter.objects.filter(name=shelter.name).exists():
        shel = Shelter.objects.get(name=shelter.name)
        for dog in Animal.objects.filter(shelter=shel):
            listings_in_db.add(dog.link)
    else:
        shel = Shelter(
            name=shelter.get_name(),
            address=shelter.get_address(),
            city=shelter.get_address(),
            phone=shelter.get_phone(),
            email=shelter.get_email(),
            website=shelter.get_website(),
        )

        shel.save()
    dogs_from_website = shelter.get_all_dogs_from_website()

    nonvalid = listings_in_db - dogs_from_website
    new_dogs = dogs_from_website - listings_in_db
    for dog in new_dogs:
        dog = dog_class(dog, "dog", shelter)
        dog.download_dog_link_content()
        dog.set_dog_details()
        dog.set_dog_pictures()
        ani = Animal(
            name=dog.get_name(),
            age=dog.get_age(),
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
    for dog in nonvalid:
        ani = Animal.objects.get(link=dog)
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
