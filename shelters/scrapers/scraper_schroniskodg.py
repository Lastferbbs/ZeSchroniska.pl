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
from base_classes import Dog, Schronisko
from headers import headers


class SchroniskoDG(Schronisko):
    def __init__(self, name, address, phone, email, website, link_dogs, link_cats):
        Schronisko.__init__(
            self, name, address, phone, email, website, link_dogs, link_cats
        )

    def get_dogs_content(self, page):

        website = requests.get(self.link_dogs + page, headers=headers)
        return website.content

    def get_availables_pages_for_animal(self, type_animal):
        if type_animal == "dogs":
            soup = BeautifulSoup(self.get_dogs_content("1"), "lxml")

        # if type_animal == "cats":
        #     soup = BeautifulSoup(self.get_cats_content("1"), "lxml")

        available_pages = soup.find_all("a", "page-numbers")
        max_page_number = available_pages[-2].text
        return max_page_number

    def get_all_dogs_from_website(self):
        dogs_list = []

        for page in range(
            1, int(self.get_availables_pages_for_animal("dogs")) + 1
        ):  # iterate over all pages
            soup = BeautifulSoup(self.get_dogs_content(str(page)), "lxml")
            dogs_listings = soup.find_all("a", "cmsmasters_img_link preloader")
            for dog in dogs_listings:
                dogs_list.append(dog.attrs["href"])
        return dogs_list


class DogDG(Dog):
    def __init__(
        self,
        link,
        animal_type,
        current_place,
    ):
        Dog.__init__(self, link, animal_type, current_place)

    def download_dog_link_content(self):
        self.link_content = requests.get(self.link, headers=headers).content
        test = 1

    def parse_dog_details(self):
        description_details_parameters_setter = {
            "Data:": self.set_publication_date,
            "Orientacyjny wiek": self.set_age,  # TODO: normalize date format
            "Płeć": self.set_sex,
            "Rasa": self.set_breed,
            "Wielkość": self.set_size,
            "Kastracja/Sterylizacja": self.set_sterilized,
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
            if parameter.contents[0].text in description_details_parameters_setter:
                if (
                    parameter.contents[0].text == "Data:"
                ):  # taking last updated date which is on slot 1
                    description_details_parameters_setter[parameter.contents[0].text](
                        parameter.contents[1].contents[1].text
                    )
                else:  # taking other details which are on slot 0
                    description_details_parameters_setter[parameter.contents[0].text](
                        parameter.contents[1].contents[0].text
                    )
        pictures = soup.find_all("img", "full-width")
        for picture in pictures:
            if picture.attrs["alt"] == name:
                self.add_picture(pictures[0].attrs["src"])
        # parameter_name = soup.find_all(
        #     "span", "elementor-icon-list-text"
        # )  # get all dog's details names
        # desc = self.find_description(soup.find_all("span", "raven-heading-title"))
        # if desc:
        #     parameter.pop(
        #         1
        #     )  # remove info about quarantine from list of details, if exists
        # publication_date = self.find_last_modified_date(
        #     json.loads(soup.find("script", type="application/ld+json").text)
        # )
        # pictures = soup.find_all("img", "attachment-full size-full")

        # return parameter, parameter_name, pictures, publication_date


if __name__ == "__main__":
    shelter = SchroniskoDG(
        "schroniskodg",
        "Dłużyna Górna 1F, 59-930 Pieńsk",
        "+48 (75) 778 04 12 ",
        "schroniskodluzyna@gmail.com",
        "https://schroniskodg.pl/",
        "https://schroniskodg.pl/zw-kat/psy-do-adopcji/page/",  ### zastanowić się co ze szczeniakami
        [
            "https://schroniskodg.pl/zw-kat/koty-do-adopcji/page/",
            "https://schroniskodg.pl/zw-kat/kociaki-do-adopcji/page/",
        ],
    )
    # print(shelter.get_availables_pages_for_animal("dogs"))
    # print(shelter.get_all_dogs_from_website())
    # for dog in shelter.get_all_dogs_from_website():
    dog = DogDG("https://schroniskodg.pl/zwierzak/andrut/", "pies", shelter)
    shelter.add_dog(dog)
    dog.download_dog_link_content()
    dog.parse_dog_details()
    # dog.set_dog_pictures()
    dog.print_dog_details()
