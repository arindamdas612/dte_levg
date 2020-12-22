from django import forms
from django.core.validators import RegexValidator

from django.contrib.auth.forms import PasswordChangeForm


from .models import FyDataSummary


class AddFYDataForm(forms.Form):
    data_file = forms.FileField(label='File to check', widget=forms.FileInput(attrs={
        'class': 'form-control-file',
        'accept': '.xlsx',
    }))
    year = forms.IntegerField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeHolder': 'Year'}),)
    period = forms.IntegerField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeHolder': 'Period'}),)

    def is_valid(self):
        valid = super(AddFYDataForm, self).is_valid()
        if not valid:
            return valid
        data = self.cleaned_data
        filename = data['data_file'].name
        ext = filename.split('.')[-1]
        if ext != 'xlsx':
            self._errors[
                'data_file'] = ' - Invalid file type, only zipped file with extension (.xlsx) allowed.'
            return False
        return True


class FileViewForm(forms.Form):
    file_to_view = forms.ChoiceField(choices=[(data.id, data.display_filename()) for data in FyDataSummary.objects.all().order_by('-create_ts')],
                                     required=True, widget=forms.Select(attrs={'class': 'form-control form-control-lg'}),)


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': "Old Password"})
        self.fields['new_password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': "New Password"})
        self.fields['new_password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': "Retype New Password"})

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
