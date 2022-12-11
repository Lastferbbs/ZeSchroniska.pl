from scrapers import scaper_otozschroniskozg


shelter = scaper_otozschroniskozg.OtozSchroniskoZg(
        "otozschroniskozg",
        "Zielona Góra",
        "577 466 576",
        "zielonagora@otoz.pl",
        "http://otozschroniskozg.pl/",
        "http://otozschroniskozg.pl/psy-do-adopcji?jsf=jet-engine:all-dogs&pagenum=",
        "http://otozschroniskozg.pl/koty-do-adopcji?jsf=jet-engine:all-cats&pagenum=",
    )
    shel = Shelter(
        name=shelter.get_name(),
        address=shelter.get_address(),
        city=shelter.get_address(),
        phone=shelter.get_phone(),
        email=shelter.get_email(),
        website=shelter.get_website(),
    )


if __name__ == "__main__":
    scrap_test(None)
