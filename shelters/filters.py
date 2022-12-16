import django_filters
from .models import Animal
from .consts import SIZE_OPTIONS
from django import forms

choices = [("rasowe", "Rasowe")]

distance = [
    ("10", "10 km"),
    ("20", "20 km"),
    ("30", "30 km"),
    ("70", "50 km"),
    ("100", "100 km"),
    ("200", "200 km"),
]


sterylizacja = [("tak", "Tak"), ("nie", "Nie")]

plec = [("pies", "Samiec"), ("suka", "Samica")]


class AnimalFilter(django_filters.FilterSet):
    # name = django_filters.CharFilter(lookup_expr="iexact")
    size = django_filters.MultipleChoiceFilter(
        choices=SIZE_OPTIONS,
        widget=forms.CheckboxSelectMultiple(),
        label="Wielkość",
    )

    breed = django_filters.MultipleChoiceFilter(
        method="filter_published",
        choices=choices,
        widget=forms.CheckboxSelectMultiple(),
        lookup_expr="icontains",
        field_name="breed",
        label="Rasa",
    )

    sterilized = django_filters.MultipleChoiceFilter(
        choices=sterylizacja,
        widget=forms.CheckboxSelectMultiple(),
        lookup_expr="icontains",
        field_name="sterilized",
        label="Wysterylizowany",
    )

    sex = django_filters.MultipleChoiceFilter(
        choices=plec,
        widget=forms.CheckboxSelectMultiple(),
        lookup_expr="icontains",
        field_name="sex",
        label="Płeć",
    )

    city = django_filters.CharFilter(
        lookup_expr="iexact",
        field_name="shelter__phone",
        label="Twoja lokalizacja",
        exclude=True,
    )

    distance = django_filters.ChoiceFilter(
        lookup_expr="iexact",
        label="Maksymalna odległość od twojej lokalizacji",
        field_name="shelter__city",
        choices=distance,
        exclude=True,
    )

    # TODO: Add age filter

    def filter_published(self, queryset, name, value):
        # construct the full lookup expression.
        return (
            queryset.exclude(breed="Brak danych")
            .exclude(breed="mieszana")
            .exclude(breed="mieszaniec")
            .exclude(breed="Brak informacji")
            .filter(breed__icontains="")
        )


# class ShelterFilter(django_filters.FilterSet):
#     # name = django_filters.CharFilter(lookup_expr="iexact")
#     city = django_filters.CharFilter(lookup_expr="iexact")
#     # distance = django_filters.CharFilter(lookup_expr="iexact")

#     class Meta:
#         model = Animal
#         fields = ["city"]
#         form = DistanceForm
