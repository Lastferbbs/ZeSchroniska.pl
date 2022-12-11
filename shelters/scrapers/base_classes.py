import requests
import os
from django.conf import settings

# file_path = os.path.join(settings.BASE_DIR, "relative_path")

# file_path = os.path.join(
#     settings.BASE_DIR, "Zeschroniska.pl/zeschroniska/shelters/scrapers/"
# )
# from .headers import headers


class Schronisko(object):
    def __init__(self, name, address, phone, email, website, link_dogs, link_cats):
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.website = website
        self.link_dogs = link_dogs
        self.link_cats = link_cats
        self.dogs = []
        self.cats = []

    def get_name(self):
        return self.name

    def get_address(self):
        return self.address

    def get_phone(self):
        return self.phone

    def get_email(self):
        return self.email

    def get_website(self):
        return self.website

    def get_dogs_content(self, page):
        website = requests.get(self.link_dogs + page, headers=headers)
        return website.content

    def get_cats_content(self, page):
        website = requests.get(self.link_cats + page, headers=headers)
        return website.content

    def get_dogs(self):
        return self.dogs

    def get_cats(self):
        return self.cats

    def add_dog(self, dog):
        self.dogs.append(dog)

    def add_cat(self, cat):
        self.cats.append(cat)

    def __str__(self):
        return (
            self.name
            + " "
            + self.address
            + " "
            + self.phone
            + " "
            + self.email
            + " "
            + self.website
        )

    def __repr__(self):
        return (
            self.name
            + " "
            + self.address
            + " "
            + self.phone
            + " "
            + self.email
            + " "
            + self.website
        )

    def __unicode__(self):
        return (
            self.name
            + " "
            + self.address
            + " "
            + self.phone
            + " "
            + self.email
            + " "
            + self.website
        )

    def __eq__(self, other):
        return self.name == other.name and self.website == other.website

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.name.__hash__()

    def scrap_all_animals(self):

        return self.name

    def scrap_new_animals(self):
        return self.name


class Animal:
    def __init__(self, link, animal_type, current_place):
        self.link = link
        self.animal_type = animal_type
        self.current_place = current_place


class Dog(
    Animal
):  # dodac klase Dog z konkretnego schroniska, ktora dziedziczy po klasie Dog
    def __init__(
        self,
        link,
        animal_type,
        current_place,
        name="Brak danych",
        sex="Brak danych",
        breed="Brak danych",
        description="\n",
        size="Brak danych",
        age="Brak danych",
        sterilized="Brak danych",
        link_content=None,
    ):
        Animal.__init__(self, link, animal_type, current_place)
        self.name = name
        self.sex = sex
        self.breed = breed
        self.description = description
        self.size = size
        self.age = age
        self.pictures = []
        self.link_content = link_content
        self.publication_date = None
        self.sterilized = sterilized

    def get_name(self):
        return self.name

    def get_sex(self):
        return self.sex

    def get_breed(self):
        return self.breed

    def get_description(self):
        return self.description

    def get_size(self):
        return self.size

    def get_age(self):
        return self.age

    def get_pictures(self):
        return self.pictures

    def get_link(self):
        return self.link

    def get_animal_type(self):
        return self.animal_type

    def get_current_place(self):
        return self.current_place

    def get_publication_date(self):
        return self.publication_date

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def set_sex(self, sex):
        self.sex = sex

    def set_size(self, size):
        self.size = size

    def set_age(self, age):
        self.age = age

    def set_breed(self, breed):
        self.breed = breed

    def set_publication_date(self, publication_date):
        self.publication_date = publication_date

    def set_sterilized(self, sterilized):
        self.sterilized = sterilized

    def add_picture(self, picture):
        self.pictures.append(picture)

    def print_dog_details(self):
        print("Imię: " + self.name)
        print("Płeć: " + self.sex)
        print("Wielkość: " + self.size)
        print("Wiek: " + self.age)
        print("Rasa: " + self.breed)
        print("Opis: " + self.description)
        print("Link: " + self.link)
        print("Zdjęcia: " + str(self.pictures))
        print("Schronisko: " + self.current_place.name)
        print("Data publikacji: ", self.publication_date)

    def get_dog_details(self):
        return (
            self.name,
            self.sex,
            self.size,
            self.age,
            self.breed,
            self.description,
            self.link,
            self.pictures,
            self.current_place.get_website(),
            self.publication_date,
        )
