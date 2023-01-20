from bs4 import BeautifulSoup
import requests
import json
import re
from datetime import datetime


import os
from django.conf import settings

# file_path = os.path.join(settings.BASE_DIR, "relative_path")

# file_path = os.path.join(
#     settings.BASE_DIR, "Zeschroniska.pl/zeschroniska/shelters/scrapers/"
# )
import sys

sys.path.append("/home/bsc-node/sol_exp/Zeschroniska.pl/zeschroniska")
from shelters.scrapers.base_classes import Animal, Schronisko
from shelters.scrapers.headers import headers


class SchroniskoKroto(Schronisko):
    def __init__(
        self,
        name="schroniskokrotoszyn",
        address="ul. Ceglarska 11, 63-700 Krotoszyn",
        city="Krotoszyn",
        phone="+48 660 662 191",
        email="krotoszyn@eadopcje.org",
        website="https://krotoszyn.eadopcje.org/",
        link_dogs="https://krotoszyn.eadopcje.org/psy/aktywne/do_adopcji/wszystkie/wszystkie/",
        link_cats="https://krotoszyn.eadopcje.org/koty/aktywne/do_adopcji/wszystkie/wszystkie/",
    ):
        Schronisko.__init__(
            self, name, address, phone, email, website, link_dogs, link_cats, city
        )

    def get_animals_content(self, page, type_animal):
        if type_animal == "dogs":
            website = requests.get(self.link_dogs + page, headers=headers)
            return website.content

        elif type_animal == "cats":
            website = requests.get(self.link_cats + page, headers=headers)
            return website.content

    def get_dogs_content(self, page):
        return self.get_animals_content(page, "dogs")

    def get_cats_content(self, page):
        return self.get_animals_content(page, "cats")

    def get_availables_pages_for_animal(self, type_animal):
        if type_animal == "dogs":
            soup = BeautifulSoup(self.get_dogs_content("10"), "lxml")
            return self.find_max_page(soup)

        elif type_animal == "cats":
            soup = BeautifulSoup(self.get_cats_content("10"), "lxml")
            return self.find_max_page(soup)

    def find_max_page(self, soup):
        available_pages = soup.find_all(
            "a",
            href=lambda href: href
            and "aktywne/do_adopcji/wszystkie/wszystkie/" in href,
        )
        if not available_pages:
            return 0
        max_page_numbers = available_pages[-1].text
        return max_page_numbers

    def get_all_dogs_from_website(self):
        return self.get_all_animals_from_website("dogs", "psiak/")

    def get_all_cats_from_website(self):
        return self.get_all_animals_from_website("cats", "kot/")

    def get_all_animals_from_website(self, type_animal, regex_animal):
        animal_list = set()
        pages_number = self.get_availables_pages_for_animal(type_animal)
        if int(pages_number) > 0:
            for page in range(1, int(pages_number) + 1):  # iterate over all pages
                soup = BeautifulSoup(
                    self.get_animals_content(str((page - 1) * 10), type_animal),
                    "lxml",
                )

                animal_listings = soup.find_all("a", href=re.compile(regex_animal))
                for animal in animal_listings[::2]:
                    animal_list.add(
                        "https://krotoszyn.eadopcje.org/" + animal.attrs["href"]
                    )
        return animal_list


class AnimalKrotoszyn(Animal):
    def __init__(
        self,
        link,
        animal_type,
        current_place,
    ):
        Animal.__init__(self, link, animal_type, current_place)

    def download_animal_link_content(self):
        self.link_content = requests.get(self.link, headers=headers).content

    def set_animal_details(self):

        soup = BeautifulSoup(self.link_content, "lxml")
        content = soup.find("table", style="width:;").find_all("tr")
        debug = 1

        name = content[1].contents[3].contents[10][1:]
        sex = content[1].contents[3].contents[13][1:]
        age = content[1].contents[3].contents[16][1:]
        if self.animal_type == "dog":
            description = content[3].text
            description = description.replace("\n", "").replace("\r", " ")
            sterilization = content[4].contents[1].contents[3][1:]
            self.set_sterilized(sterilization)
        else:
            description = content[2].text
            description = description.replace("\n", "").replace("\r", " ")

        print(name, sex, age, description)
        # TODO: nie dziala, date trzeba poprawic:
        if len(content[0].contents[1].contents) > 8:
            date = datetime.strptime(
                content[0].contents[1].contents[2].text[-10:], "%d.%m.%Y"
            ).date()
        else:
            date = datetime.strptime(
                content[0].contents[1].contents[1][-10:], "%d.%m.%Y"
            ).date()

        self.set_name(name)
        self.set_sex(sex)
        self.set_age(age)
        self.set_description(description)
        self.set_publication_date(date)

        # self.set_name(name)
        # if soup.find("div", style="text-align: justify;"):
        #     description = soup.find("div", style="text-align: justify;").text
        # else:
        #     description = soup.find(
        #         "div",
        #         "col-sm-12 col-md-6 col-md-pull-6 col-lg-7 col-lg-pull-5 profile-description-sub-content",
        #     ).text

        # self.set_description(description)
        # parameters = soup.find(
        #     "table", "table table-profile-description", "tr"
        # )  # get all dog's details
        # date = datetime.strptime(
        #     parameters.contents[3].contents[3].text, "%Y-%m-%d"
        # ).date()
        # self.set_publication_date(date)
        # self.set_in_shelter_from(date)
        # if "duże" in parameters.contents[5].contents[3].text:
        #     self.set_size("średni")
        # else:
        #     self.set_size("mały")
        # if "Suczki" in parameters.contents[5].contents[3].text:
        #     self.set_sex("samica")
        # elif "Psy" in parameters.contents[5].contents[3].text:
        #     self.set_sex("samiec")
        # else:
        #     self.set_sex("Brak danych")
        # self.set_age_in_months()

    def set_animal_pictures(self):
        soup = BeautifulSoup(self.link_content, "lxml")
        pictures = soup.find_all("a", href=re.compile("/galeria/"))
        for picture in pictures[::2]:
            self.add_picture(
                "https://krotoszyn.eadopcje.org/" + picture.attrs["href"][2:]
            )


# # # print(shelter.get_availables_pages_for_animal("dogs"))
# # # print(shelter.get_availables_pages_for_animal("cats"))
# # # print(shelter.get_all_dogs_from_website())
# # # print(shelter.get_all_cats_from_website())
shelter = SchroniskoKroto()
# print(shelter.get_all_dogs_from_website())
# TODO: przetestowac pobieranie kotow
print(shelter.get_all_cats_from_website())


psiak = AnimalKrotoszyn("https://krotoszyn.eadopcje.org/kot/116", "kot", shelter)
psiak.download_animal_link_content()
psiak.set_animal_details()
psiak.set_animal_pictures()
# psiak.set_animal_pictures()
# psiak.print_animal_details()
