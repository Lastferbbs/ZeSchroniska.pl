from django.db import models
from .consts import SIZE_CHOICES

# Create your models here.


class Shelter(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    website = models.CharField(max_length=200, primary_key=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Animal(models.Model):
    name = models.CharField(max_length=200)
    age = models.CharField(max_length=200)
    age_in_months = models.FloatField(default=1000)
    sex = models.CharField(max_length=200)
    breed = models.CharField(max_length=200)
    description = models.CharField(max_length=5000)
    pictures = models.CharField(max_length=2000)
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE)
    publication_date = models.DateField(max_length=200, choices=SIZE_CHOICES)
    size = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    animal_type = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    sterilized = models.CharField(max_length=200, default="Brak danych")
    valid = models.BooleanField(default=True)
    in_shelter_from = models.CharField(max_length=200, default="Brak danych")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    # def Meta(self):
    #     ordering = ["-created_at"]

    def first_picture(self):
        return self.pictures.split(",")[0]
