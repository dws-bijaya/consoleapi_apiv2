from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

def index(request):
 return HttpResponse('Welcome to the Tinyapp\'s Homepage!')

urlpatterns = [
    path(r'', index), #admin.site.urls)
    path(r'^.*/$', index)
]
#https://apiv2.example.com/{class}/{method}/{apikey=}/[[param1/[param2/[..]]]