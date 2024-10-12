from django import forms
from .models import Exploitant
from django.core.exceptions import ValidationError
from datetime import date, timedelta

class ExploitantForm(forms.ModelForm):
    class Meta:
        model = Exploitant
        fields = ['nom', 'post_nom', 'prenom', 'sexe', 'lieu_naissance', 'date_naissance', 'etat_civil', 'nom_conjoint', 'nb_enfants', 'adresse', 'niveau_etude', 'fonction', 'telephone', 'photo']
        exclude = ['qrcode', 'date_enregistrement', 'date_mise_a_jour']

    nom = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    post_nom = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    prenom = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    sexe = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=Exploitant.SEXE_CHOICES)
    lieu_naissance = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_naissance = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%d-%m-%Y'] ) # Le format pour les entrées  
    etat_civil = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=Exploitant.ETAT_CIVIL_CHOICES) 
    nom_conjoint = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    nb_enfants = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    adresse = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    niveau_etude = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=Exploitant.NIVEAU_ETUDE_CHOICES)
    fonction = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=Exploitant.FONCTION_CHOICES)
    telephone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    photo = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), required=False)

    def clean_nb_enfants(self):
        nb_enfants = self.cleaned_data.get('nb_enfants')
        if nb_enfants is not None and nb_enfants < 0:
            raise forms.ValidationError("Le nombre d'enfants ne peut pas être négatif.")
        return nb_enfants

    def clean_date_naissance(self):
        date_naissance = self.cleaned_data.get('date_naissance')
        if date_naissance:
            today = date.today()
            minimum_date = today - timedelta(days=18*365)
            if date_naissance > minimum_date:
                raise ValidationError("Vous devez avoir au moins 18 ans.")
        return date_naissance

    
####################################################################################################################
# forms.py
from django import forms
from .models import UploadFile

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ['file']


#####################################################################################################################

# enregistrement/forms.py
from django import forms
from .models import Incident

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = '__all__'

