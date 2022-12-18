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

# TODO - brak podstrony dla zwierzaka, jakoś to spróbować obejść
class SchroniskoWro(Schronisko):
    def __init__(
        self,
        name="schroniskowroclaw",
        address="ul. Ślazowa 2, 51-007 Wrocław",
        city="Wrocław",
        phone="+48 71 362 56 74",
        email="schronisko.ola@gmail.com",
        website="https://www.schroniskowroclaw.pl/",
        link_dogs=(
            "https://www.schroniskowroclaw.pl/adopcja/psy-do-adopcji-c2?page=",
            "https://www.schroniskowroclaw.pl/adopcja/suczki-c5?page=",
        ),
        link_cats="https://www.schroniskowroclaw.pl/adopcja/koty-c9?page=",
    ):
        Schronisko.__init__(
            self, name, address, phone, email, website, link_dogs, link_cats, city
        )

    def get_female_content(self, page):
        website = requests.get(self.link_dogs[1] + page, headers=headers)
        return website.content

    def get_dogs_content(self, page):
        website1 = requests.get(self.link_dogs[0] + page, headers=headers)
        return website1.content

    def get_cats_content(self, page):
        website = requests.get(self.link_cats + page, headers=headers)
        return website.content

    def get_availables_pages_for_animal(self, type_animal):
        if type_animal == "dogs":
            max_page_numbers = []
            soup = BeautifulSoup(self.get_dogs_content("1"), "lxml")
            available_pages = soup.find("ul", "pagination", "li")
            max_page_numbers.append(available_pages.contents[-2].text)
            soup = BeautifulSoup(self.get_female_content("1"), "lxml")
            available_pages = soup.find("ul", "pagination", "li")
            max_page_numbers.append(available_pages.contents[-2].text)
            return max_page_numbers

        elif type_animal == "cats":
            soup = BeautifulSoup(self.get_cats_content("1"), "lxml")

            available_pages = soup.find("ul", "pagination", "li")
            max_page_number = available_pages.contents[-2].text
            return max_page_number

    def get_all_dogs_from_website(self):
        dogs_list = set()

        for i in range(len(self.link_dogs)):
            for page in range(
                1, int(self.get_availables_pages_for_animal("dogs")[i]) + 1
            ):  # iterate over all pages
                if i == 0:
                    soup = BeautifulSoup(self.get_dogs_content(str(page)), "lxml")
                else:
                    soup = BeautifulSoup(self.get_female_content(str(page)), "lxml")
                dogs_listings = soup.find_all("a", "thumbnail")
                for dog in dogs_listings:
                    dogs_list.add(dog.attrs["href"])
        return dogs_list

    def get_all_cats_from_website(self):
        cats_list = set()

        for page in range(1, int(self.get_availables_pages_for_animal("cats")) + 1):
            soup = BeautifulSoup(self.get_cats_content(str(page)), "lxml")
            cats_listings = soup.find_all("a", "thumbnail")
            for cat in cats_listings:
                cats_list.add(cat.attrs["href"])
        return cats_list


class AnimalWro(Animal):
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

        soup = BeautifulSoup(self.link_content, "lxml")
        name = soup.find("h3", "h-serif-flex").text
        self.set_name(name)
        if soup.find("div", style="text-align: justify;"):
            description = soup.find("div", style="text-align: justify;").text
        else:
            description = soup.find(
                "div",
                "col-sm-12 col-md-6 col-md-pull-6 col-lg-7 col-lg-pull-5 profile-description-sub-content",
            ).text

        self.set_description(description)
        parameters = soup.find(
            "table", "table table-profile-description", "tr"
        )  # get all dog's details
        date = datetime.strptime(
            parameters.contents[3].contents[3].text, "%Y-%m-%d"
        ).date()
        self.set_publication_date(date)
        self.set_in_shelter_from(date)
        if "duże" in parameters.contents[5].contents[3].text:
            self.set_size("średni")
        else:
            self.set_size("mały")
        if "Suczki" in parameters.contents[5].contents[3].text:
            self.set_sex("samica")
        elif "Psy" in parameters.contents[5].contents[3].text:
            self.set_sex("samiec")
        else:
            self.set_sex("Brak danych")
        self.set_age_in_months()

    def set_animal_pictures(self):
        soup = BeautifulSoup(self.link_content, "lxml")
        pictures = soup.find("a", "thumbnail")
        self.add_picture(pictures.attrs["href"])


# # # print(shelter.get_availables_pages_for_animal("dogs"))
# # # print(shelter.get_availables_pages_for_animal("cats"))
# # # print(shelter.get_all_dogs_from_website())
# # # print(shelter.get_all_cats_from_website())
# shelter = SchroniskoWro()
# psiak = AnimalWro(
#     "https://www.schroniskowroclaw.pl/adoptuj/karol-i2058", "pies", SchroniskoWro()
# )
# psiak.download_animal_link_content()
# psiak.set_animal_details()
# psiak.set_animal_pictures()
# psiak.print_animal_details()
