"""apiv2 URL Configuraesponse

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
from plugins.pingpong    import PingPong


def home(request):
 return HttpResponse('Welcome to the Tinyapp\'s Homepage!')



urlpatterns = [
	path('pingpong/test/<slug:apikey>/', PingPong.test), #include('pingpong.urls')), #admin.site.urls)
    path('ping/pong/<slug:apikey>/', PingPong.pong) 

    #path(r'', home), #admin.site.urls)
    #path(r'^.*/$', home)
]
