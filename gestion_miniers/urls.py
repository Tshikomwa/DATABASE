from django.contrib import admin
from django.urls import include, path
from enregistrement.views import accueil  # Ajoutez cet import
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accueil, name='accueil'),  # Empty path for the root URL
    path('enregistrement/', include('enregistrement.urls')),

]
