# Django
from django import forms

class NoteForm(forms.Form):
    """
    Form for notebox
    """


    # <textarea id="note-textarea" name="note" rows="5" maxlength: "2000"
    #         placeholder="Relax and take notes" autofocus="autofocus"> 
    note = forms.CharField(widget=forms.Textarea(attrs={
            'autofocus': 'autofocus',
            'id': 'note-textarea',
            'name': 'note',
            'rows': '5',
            'placeholder': 'Relax and take notes',
            'maxlength': '2000'
            }
        ))


    # <input type="password" id="key-input" maxlength="60" placeholder="Your key"> 
    key = forms.CharField(widget=forms.PasswordInput(
        attrs={
                'id': 'key-input',
                'maxlength': '60',
                'placeholder': 'Your key'
            }
        ))

class KeyForm(forms.Form):
    key = forms.CharField(widget=forms.PasswordInput(
        attrs={
                'id': 'key-submit',
                'maxLength': '60',
                'placeholder': 'Your key'
            }
        ))


class SearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(attrs={
            'autofocus': 'autofocus',
            'id': 'search-textinput',
            'name': 'search',
            'placeholder': 'Search notes',
            'maxlength': '50',
            'type': 'search',
            }))
