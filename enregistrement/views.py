# enregistrement/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ExploitantForm
from .models import Exploitant
import qrcode
from io import BytesIO
from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Exploitant
from django.shortcuts import render, redirect
from .forms import ExploitantForm
from .models import Exploitant
from django.utils import timezone
from django.http import HttpResponse
from django.forms import modelform_factory
from django.utils import timezone  # Importez le module timezone
from django.http import HttpResponse
from PIL import Image
from io import BytesIO
from enregistrement.models import Exploitant
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


# Page d'acceuil

def accueil(request):
    return render(request, 'enregistrement/accueil.html')

#################################################################################################
#################################################################################################

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

def get_qrcode(request, pk):
    # Récupérer l'exploitant avec le pk
    exploitant = get_object_or_404(Exploitant, pk=pk)

    # Assurez-vous que le code est généré si ce n'est pas déjà fait
    if not exploitant.code:
        exploitant.save()  # Cela va générer le code si nécessaire

    # Générer le QR code après avoir vérifié et sauvegardé le code
    img = generate_qrcode(exploitant)

    # Créer la réponse HTTP pour retourner l'image QR code au format PNG
    response = HttpResponse(img, content_type="image/png")
    return response

#################################################################################################
import qrcode
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.http import HttpResponse

def generate_qrcode(exploitant, extra_info=None, size=200):
    # Assurez-vous que la date est bien formatée en 'd-m-Y'
    date_enregistrement_formatee = exploitant.date_enregistrement.strftime('%d-%m-%Y')

    # Générer le contenu du QR code basé sur les informations de l'exploitant
    content = f"Code: {exploitant.code}\nNom: {exploitant.nom}\nPost-Nom: {exploitant.post_nom}\nPrénom: {exploitant.prenom}\n"
    content += f"Lieu de naissance: {exploitant.lieu_naissance}\nDate de naissance: {exploitant.date_naissance.strftime('%d-%m-%Y')}\n"
    content += f"Fonction: {exploitant.fonction}\nDate d'enregistrement: {date_enregistrement_formatee}\n"

    # Ajouter des informations supplémentaires si fournies
    if extra_info:
        content += f"Information supplémentaire: {extra_info}\n"

    # Créer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size))

    # Convertir l'image en bytes
    image_stream = BytesIO()
    img.save(image_stream, format='PNG')
    image_stream.seek(0)  # Rewind the stream to the beginning

    return ContentFile(image_stream.getvalue(), f'qrcode_{exploitant.pk}.png')




#################################################################################################
def recording(request):
    enregistrement_reussi = False
    echec_enregistrement = False

    if request.method == 'POST':
        form = ExploitantForm(request.POST, request.FILES)
        if form.is_valid():
            exploitant = form.save(commit=False)
            
            # Remplir les champs date_enregistrement et date_mise_a_jour avec uniquement la date
            exploitant.date_enregistrement = timezone.now().date()
            exploitant.date_mise_a_jour = timezone.now().date()

            # Formater la date en (d-m-Y) lors de l'affichage ou d'une opération spécifique
            date_enregistrement_formattee = exploitant.date_enregistrement.strftime('%d-%m-%Y')
            date_mise_a_jour_formattee = exploitant.date_mise_a_jour.strftime('%d-%m-%Y')

            # Sauvegardez une première fois pour générer le code si nécessaire
            exploitant.save()

            # Générer le QR code après que le code ait été généré
            qr_code = generate_qrcode(exploitant)
            exploitant.qrcode.save(f'qrcode_{exploitant.pk}.png', qr_code)

            # Sauvegarder à nouveau après l'ajout du QR code
            exploitant.save()

            enregistrement_reussi = True
            return redirect('visualisation')
        else:
            echec_enregistrement = True
    else:
        form = ExploitantForm()

    return render(request, 'enregistrement/recording.html', {'form': form, 'enregistrement_reussi': enregistrement_reussi, 'echec_enregistrement': echec_enregistrement})

##################################################################################################
# Vue pour afficher la liste de toutes les instances Exploitant
from django.db.models import Q

def visualisation(request):
    # Récupérer tous les exploitants
    exploiteurs = Exploitant.objects.all()

    # Calculer le nombre total d'exploitants
    total_exploitants = exploiteurs.count()

    # Récupérer la valeur de recherche depuis la requête GET
    search_query = request.GET.get('search', '')

    # Si une recherche est effectuée
    if search_query:
        try:
            # Essayez de convertir la recherche en un entier
            search_query_int = int(search_query)

            # Ajoutez une vérification pour ignorer la recherche si elle est un chiffre
            if str(search_query_int) == search_query:
                raise ValueError

            # Filtrez les exploitants en fonction des critères de recherche, y compris le numéro d'ordre
            exploiteurs = exploiteurs.filter(
                Q(nom__icontains=search_query) |
                Q(post_nom__icontains=search_query) |
                Q(prenom__icontains=search_query) |
                Q(numero_ordre=search_query_int)
            )
        except ValueError:
            # La recherche n'est pas un entier, filtrez uniquement par nom, post_nom et prenom
            exploiteurs = exploiteurs.filter(
                Q(nom__icontains=search_query) |
                Q(post_nom__icontains=search_query) |
                Q(prenom__icontains=search_query)
            )

    # Passer les données dans le contexte du rendu du template
    context = {
        'exploiteurs': exploiteurs,
        'total_exploitants': total_exploitants,
        'search_query': search_query,
    }

    return render(request, 'enregistrement/visualisation.html', context)

#################################################################################################

# Vue pour supprimer un exploitant
def delete_exploitant(request, exploitant_id):
    exploiteur = get_object_or_404(Exploitant, id=exploitant_id)

    if request.method == 'POST':
        exploiteur.delete()
        return redirect('visualisation')

    return render(request, 'enregistrement/delete_exploitant.html', {'exploiteur': exploiteur})

#################################################################################################

import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import modelform_factory
from django.utils import timezone

def update_exploitant(request, exploitant_id):
    exploiteur = get_object_or_404(Exploitant, id=exploitant_id)

    ExploitantForm = modelform_factory(Exploitant, exclude=['qrcode', 'date_enregistrement', 'date_mise_a_jour'])

    modification_reussie = False  # Ajout de la variable de confirmation

    if request.method == 'POST':
        form = ExploitantForm(request.POST, request.FILES, instance=exploiteur)
        if form.is_valid():
            # Mettez à jour la date de mise à jour avant de sauvegarder
            exploiteur.date_mise_a_jour = timezone.now()
            exploiteur.save()

            modification_reussie = True  # Indique que la modification a réussi

            return redirect('visualisation')
    else:
        form = ExploitantForm(instance=exploiteur)

    context = {
        'form': form,
        'exploiteur': exploiteur,
        'modification_reussie': modification_reussie,  # Ajout de la variable au contexte
    }

    return render(request, 'enregistrement/update_exploitant.html', context)

#################################################################################################

def get_image(request, exploitant_id, field_name):
    exploiteur = Exploitant.objects.get(id=exploitant_id)

    if field_name == 'photo':
        field_data = exploiteur.photo
    elif field_name == 'qrcode':
        field_data = exploiteur.qrcode
    else:
        return HttpResponse("Invalid field name", status=400)

    # Assurez-vous que le champ de l'image est un fichier
    if not field_data:
        return HttpResponse("Image not found", status=404)

    # Ouvrez l'image depuis le chemin du fichier
    image = Image.open(field_data.path)

    # Créez un objet BytesIO pour stocker l'image redimensionnée
    image_bytes = BytesIO()

    # Déterminez le format en fonction de l'extension du fichier
    format_extension = field_data.path.split('.')[-1].lower()
    if format_extension in ['jpeg', 'jpg']:
        image_format = 'JPEG'
    elif format_extension == 'png':
        image_format = 'PNG'
    else:
        return HttpResponse("Unsupported image format", status=400)

    # Sauvegardez l'image redimensionnée dans BytesIO
    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)

    # Créez une réponse avec le contenu de BytesIO et le type de contenu approprié
    response = HttpResponse(image_bytes.read(), content_type=f"image/{image_format.lower()}")
    return response

#################################################################################################

from django.shortcuts import render, get_object_or_404
from .models import Exploitant  # Replace with your actual model name

def detail_exploitant(request, pk):
    exploitant = get_object_or_404(Exploitant, id=pk)
    return render(request, 'enregistrement/detail_exploitant.html', {'exploitant': exploitant})

#################################################################################################

from django.shortcuts import render, redirect
from .models import Incident
from .forms import IncidentForm  # Supposons que vous ayez un formulaire IncidentForm

from django.shortcuts import render, redirect
from .forms import IncidentForm  # Assuming your form is in a forms.py file in the same directory
import logging

def incident(request):
    if request.method == 'POST':
        logging.debug(request.POST)
        form = IncidentForm(request.POST)
        if form.is_valid():
            # Validate the number of cases
            nombre_cas = form.cleaned_data.get('Nombre_cas')
            if nombre_cas < 1:
                error_message = "Echec d'enregistrement: Le nombre de cas ne peut pas être inférieur à 1"
                return render(request, 'enregistrement/incident.html', {'form': form, 'error_message': error_message})

            # Save the form data
            form.save()
            return redirect('visualiser_incidents')
    else:
        form = IncidentForm()

    return render(request, 'enregistrement/incident.html', {'form': form})
#################################################################################################

def visual(request):
    incidents = Incident.objects.all()
    return render(request, 'enregistrement/visual.html', {'incidents': incidents})

# Dans votre fichier views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Incident  # Assurez-vous d'importer votre modèle Incident

#################################################################################################

def delete_incident(request, incident_id):
    # Récupérer l'incident
    incident = get_object_or_404(Incident, id=incident_id)

    if request.method == 'POST':
        # Vérifier la confirmation de suppression
        if request.POST.get('confirmation'):
            # Supprimer l'incident
            incident.delete()
            messages.success(request, 'L\'incident a été supprimé avec succès.')
            return redirect('visualiser_incidents')
        else:
            messages.error(request, 'Veuillez confirmer la suppression pour continuer.')

    return render(request, 'enregistrement/delete_incident.html', {'incident': incident})

####################################################################################################
# views.py
from django.shortcuts import render, redirect
from .models import UploadFile, Exploitant
from .forms import UploadFileForm

def upload_file(request, exploitant_id):
    exploitant = Exploitant.objects.get(id=exploitant_id)
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = form.save(commit=False)
            upload_file.exploitant = exploitant
            upload_file.save()
            return redirect('file_list', exploitant_id=exploitant_id)
    else:
        form = UploadFileForm()
    
    return render(request, 'enregistrement/upload_file.html', {'form': form, 'exploitant': exploitant})



######################################################################################
# views.py
def file_list(request, exploitant_id):
    exploitant = Exploitant.objects.get(id=exploitant_id)
    files = UploadFile.objects.filter(exploitant=exploitant)
    return render(request, 'enregistrement/file_list.html', {'files': files, 'exploitant': exploitant})

######################################################################################

def delete_file(request, file_id):
    file = get_object_or_404(UploadFile, id=file_id)
    file.delete()
    return redirect('file_list')
######################################################################################

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import UploadFile  # Modifiez en fonction de votre modèle

def download_file(request, file_id):
    file = get_object_or_404(UploadFile, id=file_id)
    file_path = file.file.path
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
    return response

##############################################################################################

from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
from django.shortcuts import get_object_or_404
from .models import Exploitant
import os
from datetime import datetime
from reportlab.lib.colors import black, red, blue
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageFilter
from PIL import Image, ImageEnhance



def generate_pdf(request, exploitant_id):
    # Récupérer les données de l'exploitant
    exploitant = get_object_or_404(Exploitant, id=exploitant_id)

    # Création du PDF en format paysage
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))  
    width, height = landscape(A4)

    from django.contrib.staticfiles import finders  # Importer finders pour localiser le fichier statique

    # Chemin pour le logo
    logo_path = finders.find('lg.jpg')  # Rechercher le fichier dans les fichiers statiques

    if logo_path:  # Si le logo est trouvé
        c.drawImage(logo_path, width - 150, height - 150, width=1.9*inch, height=2.5*inch)
    else:
        c.drawString(width - 180, height - 100, "Logo non disponible")

    # Agrandissement et placement des en-têtes, centrés sur la gauche
    c.setFont("Helvetica-Bold", 30)  # Taille augmentée pour plus de lisibilité
    c.setFillColor(black)  # Définir la couleur du texte sur noir
    c.drawCentredString(width / 2 - 65, height - 40, "REPUBLIQUE DEMOCRATIQUE DU CONGO")
    
    c.setFont("Helvetica-Bold", 19)
    c.setFillColor(red)  # Définir la couleur du texte sur rouge
    c.drawCentredString(width / 2 - 65, height - 68, "PROVINCE DU LUALABA")
    
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(blue)  # Définir la couleur du texte sur bleu
    c.drawCentredString(width / 2 - 65, height - 96, "SOCIETE COOPERATIVE MINIERE POUR LE DEVELOPPEMENT")
    
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(blue)  # Définir la couleur du texte sur bleu
    c.drawCentredString(width / 2 - 65, height - 124, "ET LE SOCIAL / (CMDS COOP-CA)")

    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(black)  # Définir la couleur du texte sur noir
    c.drawCentredString(width / 2 - 65, height - 140, "********************************************************************")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2 - 2, height - 160, "CARTE D'IDENTIFICATION DES EXPLOITANTS MINIERS ARTISANAUX")

    # Placer la photo de l'exploitant à gauche
    if exploitant.photo:
        photo_path = exploitant.photo.path
        if os.path.exists(photo_path):
            c.drawImage(photo_path, 10, height - 430, width=2.5*inch, height=3.4*inch)
        else:
            c.drawString(60, height - 430, "Photo non disponible")

    # Placer les informations à droite de la photo

    # Préparer les informations avec des parties en gras pour les valeurs
    info_lines = [
        ("NOM/POST-NOM : ", f"{exploitant.nom.upper()} / {exploitant.post_nom.upper()}"),
        ("PRÉNOM : ", f"{exploitant.prenom.upper()}"),
        ("SEXE : ", f"{exploitant.get_sexe_display().upper()}"),
        ("DATE DE NAISSANCE : ", f"{exploitant.date_naissance.strftime('%d-%m-%Y').upper()}"),
        ("ADRESSE : ", f"{exploitant.adresse.upper()}"),
        ("FONCTION : ", f"{exploitant.get_fonction_display().upper()}"),
        ("CONTACT : ", f"{exploitant.telephone.upper()}")
    ]

    # Positionner les informations sur le PDF à droite de la photo
    y_position = height - 200

    # Utiliser une police en gras pour les valeurs
    bold_font = "Helvetica-Bold"

    # Modifier la position horizontale (x) pour rapprocher du côté gauche
    x_position_label = 195  # Position horizontale pour les étiquettes
    x_position_value_offset = 10  # Décalage horizontal entre l'étiquette et la valeur
    

    for label, value in info_lines:
        # Dessiner l'étiquette avec la police normale
        c.setFont("Helvetica-Bold", 23)
        c.drawString(x_position_label, y_position, label)
        
        # Dessiner la valeur en gras
        c.setFont(bold_font, 23)
        c.drawString(x_position_label + c.stringWidth(label) + x_position_value_offset, y_position, value)
        
        # Déplacer la position verticale pour la ligne suivante
        y_position -= 38  # Espacement entre les lignes


    # Ajouter le code de l'exploitant et la date d'enregistrement en dessous des informations
    code_exploitant = exploitant.code  # Assurez-vous que ce champ existe dans votre modèle
    date_enregistrement = exploitant.date_enregistrement.strftime('%d-%m-%Y')  # Format de la date d'enregistrement

    # Modifier la police et ajuster la position pour afficher ces informations à gauche
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(red)  # Définir la couleur du texte sur rouge
    y_position -= 10  # Espacement supplémentaire avant d'ajouter ces informations

    # Afficher le code de l'exploitant à gauche
    c.drawString(20, y_position, f"CODE : {code_exploitant.upper()}")

    y_position -= 20  # Espacement pour la date d'enregistrement

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(black)  # Définir la couleur du texte sur noir
    # Afficher la date d'enregistrement à gauche, sous le code de l'exploitant
    c.drawString(20, y_position, f"Fait à Kolwezi, le {date_enregistrement}")

    # Placer le QR code à droite du nom et post-nom
    if exploitant.qrcode:
        qrcode_path = exploitant.qrcode.path
        if os.path.exists(qrcode_path):
            c.drawImage(qrcode_path, width - 140, height - 335, width=1.8*inch, height=2*inch)
        else:
            c.drawString(width - 150, height - 300, "QR Code non disponible")


    # Ajouter le logo (PNG transparent) à gauche sous les en-têtes
    logo_path = finders.find('scm.png')  # Chemin du fichier PNG

    if logo_path:  # Si le logo est trouvé
        c.drawImage(logo_path, 490, height - 576, width=4.5*inch, height=3*inch, mask='auto')  # 'mask=auto' pour gérer la transparence
    else:
        c.drawString(480, height - 578, "Logo non disponible")


    ##########################################################################################
    
    # Dessiner une nouvelle page pour le verso
    c.showPage()
    # Trouver le chemin du fichier 'fa.png' dans le répertoire static
    logo_path = finders.find('fa.png')  # Chemin du fichier PNG dans static

    # --- PLACEMENT DU FILIGRANE EN PREMIER (pour être en arrière-plan) ---
    if logo_path:  # Si le logo est trouvé
        # Charger l'image avec Pillow
        logo_image = Image.open(logo_path)

        # Convertir l'image en mode RGBA si elle ne l'est pas (pour gérer l'opacité)
        if logo_image.mode != 'RGBA':
            logo_image = logo_image.convert('RGBA')

        # Réduire l'opacité (ajuster le canal alpha) pour créer un effet de filigrane
        alpha = logo_image.split()[3]  # Extraire le canal alpha
        alpha = ImageEnhance.Brightness(alpha).enhance(0.2)  # Ajuster l'opacité (0.2 pour 20% de visibilité)
        logo_image.putalpha(alpha)  # Réappliquer le canal alpha modifié

        # Convertir l'image modifiée en un format compatible avec ReportLab
        image_io = BytesIO()
        logo_image.save(image_io, format='PNG')
        image_io.seek(0)
        watermark_logo_reader = ImageReader(image_io)

        # Dessiner l'image en tant que filigrane centrée sur toute la page
        c.drawImage(watermark_logo_reader, 0, 0, width=width, height=height, mask='auto', preserveAspectRatio=True)
    else:
        c.drawString(60, height - 500, "Logo non disponible")

    #####################################################################

    c.setFont("Helvetica-Bold", 25)
    c.setFillColor(black)  # Définir la couleur du texte sur black
    c.drawCentredString(width / 2 , height - 50, "SOCIETE COOPERATIVE MINIERE POUR LE DEVELOPPEMENT")
    
    c.setFont("Helvetica-Bold", 25)
    c.setFillColor(black)  # Définir la couleur du texte sur black
    c.drawCentredString(width / 2 , height - 85, "ET LE SOCIAL / (CMDS COOP-CA)")

    # Ajouter le logo (PNG transparent) à gauche sous les en-têtes
    logo_path = finders.find('em.png')  # Chemin du fichier PNG

    if logo_path:  # Si le logo est trouvé
        c.drawImage(logo_path, 10, height - 240, width=2.8*inch, height=2*inch, mask='auto')  # 'mask=auto' pour gérer la transparence
    else:
        c.drawString(60, height - 230, "Logo non disponible")

        # Ajouter le logo (PNG transparent) à gauche sous les en-têtes
    logo_path = finders.find('drc.png')  # Chemin du fichier PNG

    if logo_path:  # Si le logo est trouvé
        c.drawImage(logo_path, 645, height - 240, width=2.5*inch, height=2*inch, mask='auto')  # 'mask=auto' pour gérer la transparence
    else:
        c.drawString(60, height - 245, "Logo non disponible")


    # Ajouter le logo (PNG transparent) à gauche sous les en-têtes
    logo_path = finders.find('logo2.png')  # Chemin du fichier PNG

    if logo_path:  # Si le logo est trouvé
        c.drawImage(logo_path, 80, height - 530, width=10.5*inch, height=6*inch, mask='auto')  # 'mask=auto' pour gérer la transparence
    else:
        c.drawString(60, height - 500, "Logo non disponible")

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(black)  # Définir la couleur du texte sur black
    c.drawCentredString(width / 2 , height - 480, "Les autorités tant civiles que militaires sont priées d'apporter")

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(black)  # Définir la couleur du texte sur black
    c.drawCentredString(width / 2 , height - 510, "leur assistance au porteur de la présente")     

    # Finaliser le PDF
    c.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')









