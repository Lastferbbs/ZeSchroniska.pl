import django_filters
from .models import Animal
from .consts import SIZE_OPTIONS
from django import forms


class AnimalFilter(django_filters.FilterSet):
    # name = django_filters.CharFilter(lookup_expr="iexact")
    size = django_filters.MultipleChoiceFilter(
        choices=SIZE_OPTIONS,
        widget=forms.CheckboxSelectMultiple(attrs={"onchange": "this.form.submit();"}),
    )

    class Meta:
        model = Animal
        fields = {
            "size": ["exact"],
            "breed": ["exact"],
        }
