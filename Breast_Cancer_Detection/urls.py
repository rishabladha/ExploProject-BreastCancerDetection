"""Breast_Cancer_Detection URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url
from firstApp import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.registerPage , name = 'register'),
    path('login/', views.loginPage , name = 'login'),
    path('logout/', views.logoutUser, name="logout"),

    # path('admin/', admin.site.urls),
    url('home',views.index,name = 'homepage'),
    url('predictImage',views.predictImage,name = 'predictImage'),
    path('download/<int:pk>/',views.some_view,name = 'download'),
    url(r'^media/(?P<path>.*)$', serve,{'document_root':settings.MEDIA_ROOT}), 
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 
]
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)