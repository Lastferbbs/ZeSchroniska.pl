import django_filters
from .models import Animal
from .consts import (
    SIZE_CHOICES,
    BREED_CHOICES,
    DISTANCE_CHOICES,
    AGE_CHOICES,
    STERILIZED_CHOICES,
    SEX_CHOICES,
)
from django import forms


class AnimalFilter(django_filters.FilterSet):
    # name = django_filters.CharFilter(lookup_expr="iexact")
    size = django_filters.MultipleChoiceFilter(
        choices=SIZE_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        label="Wielkość",
    )

    breed = django_filters.MultipleChoiceFilter(
        method="filter_published",
        choices=BREED_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        lookup_expr="icontains",
        field_name="breed",
        label="Rasa",
    )

    sterilized = django_filters.MultipleChoiceFilter(
        choices=STERILIZED_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        lookup_expr="icontains",
        field_name="sterilized",
        label="Wysterylizowany",
    )

    sex = django_filters.MultipleChoiceFilter(
        choices=SEX_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        lookup_expr="icontains",
        field_name="sex",
        label="Płeć",
    )

    city = django_filters.CharFilter(
        lookup_expr="iexact",
        field_name="shelter__phone",
        label="Twoja lokalizacja (moze występować problem z małymi miejscowościami, można wtedy wpisać kod pocztowy)",
        exclude=True,
    )

    distance = django_filters.ChoiceFilter(
        lookup_expr="iexact",
        label="Maksymalna odległość od twojej lokalizacji",
        field_name="shelter__city",
        choices=DISTANCE_CHOICES,
        exclude=True,
    )

    name = django_filters.CharFilter(
        lookup_expr="icontains",
        field_name="name",
        label="Imię",
    )
    # TODO: skoro przy multichouice podawana jest tablica,
    # to moze warto wziac pierwszy i ostatni element i zrobic z tego zakres?
    age = django_filters.ChoiceFilter(
        field_name="age_in_months",
        label="Wiek",
        choices=AGE_CHOICES,
        method="filter_by_age",
    )

    sorting = django_filters.OrderingFilter(
        # tuple-mapping retains order
        label="SORTOWANIE",
        fields=(
            ("age_in_months", "Wiek"),
            ("publication_date", "Data opublikowania"),
        ),
        # labels do not need to retain order
        field_labels={
            "username": "User account",
        },
    )

    def filter_by_age(self, queryset, name, value):
        # construct the full lookup expression.
        # print(value)
        # print(queryset)
        value = int(value)
        if value < 4:
            gt_value = value * 12 - 12
            lt_value = value * 12
            return queryset.filter(
                age_in_months__gt=gt_value, age_in_months__lte=lt_value
            )
        elif value < 10:
            gt_value = value * 12 - 24
            lt_value = value * 12
            return queryset.filter(
                age_in_months__gt=gt_value, age_in_months__lte=lt_value
            )
        elif value == 10:
            return queryset.filter(
                age_in_months__gte=value * 12,
                age_in_months__lt=1000,
            )
        else:
            return queryset.filter(age_in_months=1000)

    def filter_published(self, queryset, name, value):
        # construct the full lookup expression.
        return (
            queryset.exclude(breed="Brak danych")
            .exclude(breed="mieszana")
            .exclude(breed="mieszaniec")
            .exclude(breed="Brak informacji")
            .filter(breed__icontains="")
        )

    # def exclude_no_info(self, queryset, name, value):
    #     return queryset.exclude(breed="Brak danych")


# class ShelterFilter(django_filters.FilterSet):
#     # name = django_filters.CharFilter(lookup_expr="iexact")
#     city = django_filters.CharFilter(lookup_expr="iexact")
#     # distance = django_filters.CharFilter(lookup_expr="iexact")

#     class Meta:
#         model = Animal
#         fields = ["city"]
#         form = DistanceForm
