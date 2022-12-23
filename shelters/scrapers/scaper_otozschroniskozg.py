import json
import re
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import requests

sys.path.append("/home/bsc-node/sol_exp/Zeschroniska.pl/zeschroniska")
from shelters.scrapers.base_classes import Schronisko, Animal

### przygotowac osobną klasę dla kazdego schroniska, ktora dziedziiczy po klasie Schronisko


class OtozSchroniskoZg(Schronisko):
    """
    A class used to represent OtozSchroniskoZg shelter

    Args:
        Schronisko (class):  Base class for shelters
    """

    def __init__(
        self,
        name="otozschroniskozg",
        address="Szwajcarska 4, 65-169 Zielona Góra",
        city="Zielona Góra",
        phone="577 466 576",
        email="zielonagora@otoz.pl",
        website="http://otozschroniskozg.pl/",
        link_dogs="http://otozschroniskozg.pl/psy-do-adopcji?jsf=jet-engine:all-dogs&pagenum=",
        link_cats="http://otozschroniskozg.pl/koty-do-adopcji?jsf=jet-engine:all-cats&pagenum=",
    ):
        """
        Constructor for OtozSchroniskoZg class with standard values

        Args:
            name (str, optional): Shelter's name. Defaults to "otozschroniskozg".
            address (str, optional): Shelter's address. Defaults to "Szwajcarska 4, 65-169 Zielona Góra".
            city (str, optional): Shelter's city. Defaults to "Zielona Góra".
            phone (str, optional): Shelter's phone number. Defaults to "577 466 576".
            email (str, optional): Shelter's email. Defaults to "zielonagora@otoz.pl".
            website (str, optional): Shelter's website. Defaults to "http://otozschroniskozg.pl/".
            link_dogs (str, optional): Link to dogs listings on shelter website. Defaults to "http://otozschroniskozg.pl/psy-do-adopcji?jsf=jet-engine:all-dogs&pagenum=".
            link_cats (str, optional):Link to cats listings on shelter website Defaults to "http://otozschroniskozg.pl/koty-do-adopcji?jsf=jet-engine:all-cats&pagenum=".
        """
        Schronisko.__init__(
            self, name, address, phone, email, website, link_dogs, link_cats, city
        )

    def get_availables_pages_for_animal(self, type_animal):
        """
        Returns number of available pages for given animal type

        Args:
            type_animal (string): Animal type, can be "dogs" or "cats"

        Returns:
            string: max number of pages on scraped website
        """
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
        """
        Returns list of all dogs from website, in form of links

        Returns:
            set: set of links to all dogs
        """
        dogs_list = set()

        for page in range(
            1, int(self.get_availables_pages_for_animal("dogs")) + 1
        ):  # iterate over all pages
            soup = BeautifulSoup(self.get_dogs_content(str(page)), "lxml")
            dogs_listings = soup.find_all("a", "jet-listing-dynamic-link__link")
            for dog in dogs_listings:
                dogs_list.add(dog.attrs["href"])
        return dogs_list

    # TODO: refactor this method, it is the same as get_all_dogs_from_website
    def get_all_cats_from_website(self):
        """
        Returns list of all cats from website, in form of links

        Returns:
            set: set of links to all cats
        """
        cats_list = set()

        for page in range(
            1, int(self.get_availables_pages_for_animal("cats")) + 1
        ):  # iterate over all pages
            soup = BeautifulSoup(self.get_cats_content(str(page)), "lxml")
            cats_listings = soup.find_all("a", "jet-listing-dynamic-link__link")
            for cat in cats_listings:
                cats_list.add(cat.attrs["href"])
        return cats_list


class AnimalOtoz(Animal):
    """
    A class used to represent Otoz animal

    Args:
        Animal (class): Base class for animals

    Attributes:
        link (string): link to animal's listing
        animal_type (string): dog or cat
        current_place (object): Shelter object, where animal is located

    """

    def __init__(
        self,
        link,
        animal_type,
        current_place,
    ):
        """
        Constructor for AnimalOtoz class

        Args:
            link (string): link to animal's listing
            animal_type (string): dog or cat
            current_place (object): Shelter object, where animal is located
        """
        Animal.__init__(self, link, animal_type, current_place)

    def download_animal_link_content(self):
        """
        Downloads content of animal's link and saves it to self.link_content
        """
        self.link_content = requests.get(self.link, verify=False).content

    def set_animal_pictures(self):
        """
        Sets animal's pictures
        """
        pictures = self.parse_animal_details()[2]
        for picture in pictures:
            self.add_picture(picture["src"])

    def find_description_place(self, list_of_site_elements):
        """
        Finds place of description in list of site elements,
        if virtual patron is in description, 1 is returned,
        if not, place of description is returned

        Args:
            list_of_site_elements (list): list of site elements

        Returns:
            int: place of description in list of site elements or 1, if virtual patron is in description
        """
        for i, element in enumerate(list_of_site_elements):
            if element.text == "Opis":
                soup = BeautifulSoup(self.link_content, "lxml")
                virtual_patron = (
                    soup.find_all(  # check if "wirtualny opiekun" is in description
                        "h2", "elementor-heading-title elementor-size-default"
                    )
                )
                if virtual_patron:  # if yes, remove it
                    return 1
                return i

    def find_last_modified_date(self, animal_date):
        """
        Returns date of last modification of animal's page,
        compares date of publication and date of last modification,
        if date of publication is older, date of last modification is returned,
        if not, date of publication is returned


        Args:
            animal_date (json): json with date of publication and date of last modification

        Returns:
            datetime: date of last modification of animal's page, in datetime format
        """
        animal_date = animal_date["@graph"][2]

        if datetime.strptime(  # if date of publication is older than date of last modification
            animal_date["datePublished"][:10],
            "%Y-%m-%d",  # [:10] because of time in date
        ) < datetime.strptime(
            animal_date["dateModified"][:10], "%Y-%m-%d"
        ):  # set date of publication to date of last modification
            last_modified_date = datetime.strptime(
                animal_date["dateModified"][:10], "%Y-%m-%d"
            ).date()
        else:
            last_modified_date = datetime.strptime(
                animal_date["datePublished"][:10],
                "%Y-%m-%d",  # else set date of publication to date of publication
            ).date()
        return last_modified_date

    def parse_animal_details(self):
        """
        Parses animal's details from link_content, returns list of details

        Returns:
            list: list of animal's details
            list: list of animal's details names
            list: list of animal's pictures
            datetime: date of last modification of animal's page, in datetime format
        """
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
        desc = self.find_description_place(soup.find_all("span", "raven-heading-title"))
        if desc:
            parameter.pop(
                1
            )  # remove info about quarantine from list of details, if exists (if opis is first element desc is 0, so it will be false)
        publication_date = self.find_last_modified_date(
            json.loads(soup.find("script", type="application/ld+json").text)
        )
        pictures = soup.find_all("img", "attachment-full size-full")

        return parameter, parameter_name, pictures, publication_date

    def set_animal_details(
        self,
    ):
        """
        Sets animal's details, checks if animal's name and description are not empty,
        """
        details = self.parse_animal_details()
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
            if "samie" in dict_details["Płeć"]:
                self.set_sex("samiec")
            elif "samic" in dict_details["Płeć"]:
                self.set_sex("samica")

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
        self.set_age_in_months()


# if __name__ == "__main__":

#     #         ,
#     #         ,
#     #
# )
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
# schronisko = OtozSchroniskoZg()
# toscik = AnimalOtoz("https://otozschroniskozg.pl/cats/ynia", "dog", schronisko)
# toscik.download_animal_link_content()
# toscik.set_animal_details()
# toscik.set_animal_pictures()
# toscik.print_animal_details()

# debug = 1
