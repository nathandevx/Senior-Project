from django import forms


class DeleteUserForm(forms.Form):
    delete_checkbox = forms.BooleanField(label='Are you sure you want to delete your account?', required=True)

    def __init__(self, *args, **kwargs):
        super(DeleteUserForm, self).__init__(*args, **kwargs)
