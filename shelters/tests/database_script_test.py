import pytest

import os
import django

import sys


django_directory = os.path.join(os.path.dirname(__file__), "../..")


sys.path.append(django_directory)
from shelters import database_script

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zeschroniska.settings")
django.setup()


def test_adding_new_animals_to_db():
    assert database_script.get_dogs_from_db() == 1


if __name__ == "__main__":
    test_adding_new_animals_to_db()
