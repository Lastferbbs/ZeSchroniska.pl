from bs4 import BeautifulSoup
import requests
import json
import re
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, "pl_PL.utf8")

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


class SchroniskoDG(Schronisko):
    def __init__(
        self,
        name="schroniskodg",
        address="Dłużyna Górna 1F, 59-930 Pieńsk",
        city="Dłużyna Górna",
        phone="+48 (75) 778 04 12 ",
        email="schroniskodluzyna@gmail.com",
        website="https://schroniskodg.pl/",
        link_dogs="https://schroniskodg.pl/zw-kat/psy-do-adopcji/page/",
        link_cats="https://schroniskodg.pl/zw-kat/koty-do-adopcji/page/",
    ):
        Schronisko.__init__(
            self, name, address, phone, email, website, link_dogs, link_cats, city
        )

    def get_dogs_content(self, page):
        website = requests.get(self.link_dogs + page, headers=headers)
        return website.content

    def get_cats_content(self, page):
        website = requests.get(self.link_cats + page, headers=headers)
        return website.content

    def get_availables_pages_for_animal(self, type_animal):
        if type_animal == "dogs":
            soup = BeautifulSoup(self.get_dogs_content("1"), "lxml")

        if type_animal == "cats":
            soup = BeautifulSoup(self.get_cats_content("1"), "lxml")

        available_pages = soup.find_all("a", "page-numbers")
        try:
            max_page_number = available_pages[-2].text
        except IndexError:
            max_page_number = 1
        return max_page_number

    def get_all_dogs_from_website(self):
        dogs_list = set()

        for page in range(
            1, int(self.get_availables_pages_for_animal("dogs")) + 1
        ):  # iterate over all pages
            soup = BeautifulSoup(self.get_dogs_content(str(page)), "lxml")
            dogs_listings = soup.find_all("a", "cmsmasters_img_link preloader")
            for dog in dogs_listings:
                dogs_list.add(dog.attrs["href"])
        return dogs_list

    def get_all_cats_from_website(self):
        cats_list = set()

        for page in range(1, int(self.get_availables_pages_for_animal("cats")) + 1):
            soup = BeautifulSoup(self.get_cats_content(str(page)), "lxml")
            cats_listings = soup.find_all("a", "cmsmasters_img_link preloader")
            for cat in cats_listings:
                cats_list.add(cat.attrs["href"])
        return cats_list


class AnimalDG(Animal):
    def __init__(
        self,
        link,
        animal_type,
        current_place,
    ):
        Animal.__init__(self, link, animal_type, current_place)

    def download_animal_link_content(self):
        self.link_content = requests.get(self.link, headers=headers).content
        test = 1

    def set_animal_details(self):
        description_details_parameters_setter = {
            "Data": self.set_publication_date,
            "Orientacyjny wiek": self.set_age,  # TODO: normalize date format
            "Płeć": self.set_sex,
            "Rasa": self.set_breed,
            "Wielkość": self.set_size,
            "Kastracja/sterylizacja": self.set_sterilized,
            "Data przyjęcia": self.set_in_shelter_from,
        }
        soup = BeautifulSoup(self.link_content, "lxml")
        name = soup.find("h3", "cmsmasters_project_title entry-title").text
        self.set_name(name)
        description = soup.find(
            "div", "cmsmasters_project_content entry-content", "p"
        ).text.replace("\n", "")
        self.set_description(description)
        parameters = soup.find_all(
            "div", "project_details_item"
        )  # get all dog's details
        for parameter in parameters:
            param = parameter.contents[0].text.replace(":", "")
            if (
                param in description_details_parameters_setter
            ):  # remove : from text, as it only appears sometimes

                if param == "Data":  # taking last updated date which is on slot 1

                    description_details_parameters_setter[param](
                        datetime.strptime(
                            parameter.contents[1].contents[1].text, "%d %B %Y"
                        )
                    )

                elif (
                    param == "Rasa"
                    and "miesz" in parameter.contents[1].contents[0].text
                ):  # breed normalization
                    description_details_parameters_setter[param]("mieszaniec")
                elif param == "Płeć":
                    if (
                        "kocur" in parameter.contents[1].contents[0].text
                        or "pies" in parameter.contents[1].contents[0].text
                    ):
                        description_details_parameters_setter[param]("samiec")
                    elif (
                        "kotka" in parameter.contents[1].contents[0].text
                        or "suka" in parameter.contents[1].contents[0].text
                    ):
                        description_details_parameters_setter[param]("samica")
                else:  # taking other details which are on slot 0
                    description_details_parameters_setter[param](
                        parameter.contents[1].contents[0].text
                    )
        self.set_age_in_months()

    def set_animal_pictures(self):
        soup = BeautifulSoup(self.link_content, "lxml")
        pictures = soup.find("div", "project_content with_sidebar")
        pictures = pictures.find_all("img")
        for picture in pictures:
            if "ares" in picture.attrs["src"]:
                self.add_picture(picture.attrs["src"])


# if __name__ == "__main__":

#     # print(shelter.get_availables_pages_for_animal("dogs"))
#     # print(shelter.get_all_dogs_from_website())
#     # for dog in shelter.get_all_dogs_from_website():
shelter = SchroniskoDG()
dog = AnimalDG("https://schroniskodg.pl/zwierzak/misiu/", "pies", shelter)
shelter.get_availables_pages_for_animal("cats")
# shelter.add_dog(dog)
# dog.download_animal_link_content()
# dog.set_animal_details()
# dog.set_animal_pictures()
# dog.print_animal_details()
