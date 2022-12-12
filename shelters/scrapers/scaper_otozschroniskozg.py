from bs4 import BeautifulSoup
import requests
import json
import re
from datetime import datetime
import os
from django.conf import settings

# file_path = os.path.join(settings.BASE_DIR, "relative_path")
import sys

sys.path.append("/home/bsc-node/sol_exp/Zeschroniska.pl/zeschroniska")
from shelters.scrapers.base_classes import Dog, Schronisko

### przygotowac osobną klasę dla kazdego schroniska, ktora dziedziiczy po klasie Schronisko


class OtozSchroniskoZg(Schronisko):
    def __init__(
        self,
        name="otozschroniskozg",
        address="Zielona Góra",
        phone="577 466 576",
        email="zielonagora@otoz.pl",
        website="http://otozschroniskozg.pl/",
        link_dogs="http://otozschroniskozg.pl/psy-do-adopcji?jsf=jet-engine:all-dogs&pagenum=",
        link_cats="http://otozschroniskozg.pl/koty-do-adopcji?jsf=jet-engine:all-cats&pagenum=",
    ):
        Schronisko.__init__(
            self, name, address, phone, email, website, link_dogs, link_cats
        )

    def get_availables_pages_for_animal(self, type_animal):
        if type_animal == "dogs":
            soup = BeautifulSoup(self.get_dogs_content("1"), "lxml")

        if type_animal == "cats":
            soup = BeautifulSoup(self.get_cats_content("1"), "lxml")

        available_pages = soup.find_all("script", id="jet-smart-filters-js-extra")
        max_page_number = re.findall("max_num_pages.*?,", str(available_pages))[0][
            :-1
        ].split(":")[1]
        return max_page_number

    def get_all_dogs_from_website(self):
        dogs_list = set()

        for page in range(
            1, int(self.get_availables_pages_for_animal("dogs")) + 1
        ):  # iterate over all pages
            soup = BeautifulSoup(self.get_dogs_content(str(page)), "lxml")
            dogs_listings = soup.find_all("a", "jet-listing-dynamic-link__link")
            for dog in dogs_listings:
                dogs_list.add(dog.attrs["href"])
        return dogs_list

    def get_all_cats_from_website(self):
        cats_list = set()

        for page in range(
            1, int(self.get_availables_pages_for_animal("cats")) + 1
        ):  # iterate over all pages
            soup = BeautifulSoup(self.get_cats_content(str(page)), "lxml")
            cats_listings = soup.find_all("a", "jet-listing-dynamic-link__link")
            for cat in cats_listings:
                cats_list.add(cat.attrs["href"])
        return cats_list


class DogOtoz(Dog):
    def __init__(
        self,
        link,
        animal_type,
        current_place,
    ):
        Dog.__init__(self, link, animal_type, current_place)

    def download_dog_link_content(self):
        self.link_content = requests.get(self.link, verify=False).content

    def set_dog_pictures(self):
        pictures = self.parse_dog_details()[2]
        for picture in pictures:
            self.add_picture(picture["src"])

    def parse_dog_details(self):
        soup = BeautifulSoup(self.link_content, "lxml")
        parameter = soup.find_all(
            "div", "jet-listing-dynamic-field__content"
        )  # get all dog's details
        parameter.insert(
            0, soup.find("h1", "jet-listing-dynamic-field__content")
        )  # add dog's name to start of list
        parameter_name = soup.find_all(
            "span", "elementor-icon-list-text"
        )  # get all dog's details names
        desc = self.find_description(soup.find_all("span", "raven-heading-title"))
        if desc:
            parameter.pop(
                1
            )  # remove info about quarantine from list of details, if exists (if opis is first element desc is 0, so it will be false)
        publication_date = self.find_last_modified_date(
            json.loads(soup.find("script", type="application/ld+json").text)
        )
        pictures = soup.find_all("img", "attachment-full size-full")

        return parameter, parameter_name, pictures, publication_date

    def find_description(self, list_of_site_elements):
        for i, element in enumerate(list_of_site_elements):
            if element.text == "Opis":
                soup = BeautifulSoup(self.link_content, "lxml")
                pictures = (
                    soup.find_all(  # check if "wirtualny opiekun" is in description
                        "h2", "elementor-heading-title elementor-size-default"
                    )
                )
                if pictures:  # if yes, remove it
                    return 1
                return i

    def find_last_modified_date(self, date_object):

        if datetime.strptime(  # if date of publication is older than date of last modification
            date_object["@graph"][2]["datePublished"][:10],
            "%Y-%m-%d",  # [:10] because of time in date
        ) < datetime.strptime(
            date_object["@graph"][2]["dateModified"][:10], "%Y-%m-%d"
        ):  # set date of publication to date of last modification
            publication_date = datetime.strptime(
                date_object["@graph"][2]["dateModified"][:10], "%Y-%m-%d"
            ).date()
        else:
            publication_date = datetime.strptime(
                date_object["@graph"][2]["datePublished"][:10],
                "%Y-%m-%d",  # else set date of publication to date of publication
            ).date()
        return publication_date

    def set_dog_details(
        self,
    ):  # wziac podstawowe parametry i przypisac im default value
        details = self.parse_dog_details()
        dict_details = {
            "Imie": details[0][0].text,
            "Opis": details[0][1].text,  # find description
        }

        i = 2  # 2 because of two first elements in details[0], which are name and description and were added before
        for element in details[1]:
            if element.text:
                if element.text == "Strona główna":
                    break

                dict_details[element.text] = details[0][i].text
                i += 1

        if dict_details["Imie"]:
            self.set_name(dict_details["Imie"])
        else:
            self.set_name("Brak informacji")

        if dict_details["Opis"]:
            self.set_description(dict_details["Opis"])
        else:
            self.set_description("Brak opisu")

        if "Płeć" in dict_details:
            self.set_sex(dict_details["Płeć"])
        else:
            self.set_sex("Brak informacji")

        if "Wielkość" in dict_details:
            self.set_size(dict_details["Wielkość"])
        else:
            self.set_size("Brak informacji")

        if "Wiek" in dict_details:
            self.set_age(dict_details["Wiek"])
        else:
            self.set_age("Brak informacji")

        if "Rasa" in dict_details:
            self.set_breed(dict_details["Rasa"])
        else:
            self.set_breed("Brak informacji")
        if details[3]:
            self.set_publication_date(details[3])

    # if __name__ == "__main__":
    #     schronisko = OtozSchroniskoZg(
    #         ,
    #         ,
    #
    #     )
    # print(schronisko.get_all_dogs_from_website())
    # for dog in schronisko.get_all_dogs_from_website():
    #     dog = DogOtoz(dog, "pies", schronisko)
    #     schronisko.add_dog(dog)
    #     dog.download_dog_link_content()
    #     dog.set_dog_details()
    #     dog.set_dog_pictures()
    #     dog.print_dog_details()

    # for element in schronisko.get_dog_details("http://otozschroniskozg.pl/dogs/gryz")[
    #     1
    # ]:
    #     print(element.text)

    # soup = BeautifulSoup(schronisko.get_cats_content("1"), "lxml")
    # available_pages = soup.find_all("script", id="jet-smart-filters-js-extra")
    # max_page_number = re.findall("max_num_pages.*?,", str(available_pages))[0][
    #     :-1
    # ].split(":")[
    #     1
    # ]  # get max number of pages
    # # page_number = available_pages[-1].attrs["data-value"]

    # for page in range(1, int(max_page_number) + 1):  # iterate over all pages
    #     soup = BeautifulSoup(schronisko.get_cats_content(str(page)), "lxml")
    #     dogs_listings = soup.find_all("a", "jet-listing-dynamic-link__link")
    #     for dog in dogs_listings:
    #         print(dog.attrs["href"])

    # dogs_listings = soup.find_all("a", "jet-listing-dynamic-link__link")
    # for dog in dogs_listings:
    #     print(dog.attrs["href"])
    # toscik = DogOtoz("https://otozschroniskozg.pl/dogs/dumka", "dog", schronisko)
    # toscik.download_dog_link_content()
    # toscik.set_dog_details()
    # toscik.set_dog_pictures()
    # toscik.print_dog_details()

    # debug = 1
