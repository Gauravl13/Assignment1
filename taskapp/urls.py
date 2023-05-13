"""employeetask URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from taskapp import views

urlpatterns = [
        path('', views.index, name='index'),
        path('login_view/', views.login_view, name='login_view'),
        path('register/', views.register, name='register'),
        path('add/', views.add_task, name='add'),
        path('search/', views.search, name='search'),
        path('home/', views.home, name='home'),
        path('delete/<int:task_id>/',views.deletedata,name="delete"),
        path('update/<int:task_id>/',views.update,name="update"),
        path('home1/', views.home_profile, name='home1'),
        path('user_register/', views.user_registration, name='user_register'),
        path('profileupdate/<str:username>/', views.profile_update, name='profileupdate'),
        path('logout/', views.logout_view, name='logout')


]
