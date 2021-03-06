"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from myapp import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'', views.index),
    url(r'^$', views.home, name='home'),
    url(r'^upload/$', views.upload, name='simple_upload'),
    url(r'^ride_stats/$', views.ride_stats, name='ride_stats'),
    url(r'^rides/$', views.rides, name='rides'),
    url(r'^register/$', views.register, name='register'),
    url(r'^end_user_agreement/$', views.terms_and_agreement, name='terms'),
    url(r'^login/$', auth_views.login, {'template_name': 'sign_in.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    #url(r'^uploads/form/$', views.model_form_upload, name='model_form_upload'),
    #url(r'^admin/', admin.site.urls),
]
