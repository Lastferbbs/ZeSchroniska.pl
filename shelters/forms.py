from django import forms

from .models import Animal


class DistanceForm(forms.Form):
    def value_from_datadict(self, data, files, name):
        getter = data.get
        # if self.allow_multiple_selected:
        #     try:
        #         getter = data.getlist
        #     except AttributeError:
        #         pass
        return getter(name)

    city = forms.CharField(
        label="Miasto",
        max_length=100,
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "np. Warszawa"}),
    )
    # distance = forms.IntegerField(
    #     label="Odległość",
    #     required=False,
    #     widget=forms.Textarea(attrs={"placeholder": "km"}),
    # )

    class Meta:
        model = Animal
        fields = ["shelter_city"]
        widgets = {"city": forms.TextInput(attrs={"placeholder": "np. Warszawa"})}

    # def __init__(self, *args, **kwargs):
    #     super(DistanceForm, self).__init__(*args, **kwargs)
    #     self.fields["city"].widget.attrs.update({"class": "form-control"})
    #     # self.fields["distance"].widget.attrs.update({"class": "form-control"})
