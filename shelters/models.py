from django.db import models

# Create your models here.


class Shelter(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    website = models.CharField(max_length=200, primary_key=True)
    active = models.BooleanField(default=True)


class Animal(models.Model):
    name = models.CharField(max_length=200)
    age = models.CharField(max_length=200)
    sex = models.CharField(max_length=200)
    breed = models.CharField(max_length=200)
    description = models.CharField(max_length=5000)
    pictures = models.CharField(max_length=2000)
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE)
    publication_date = models.CharField(max_length=200)
    size = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    animal_type = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    sterilized = models.CharField(max_length=200, default="Brak danych")

    def first_picture(self):
        return self.pictures.split(",")[0]
