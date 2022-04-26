from django.urls import path
from . import views

app_name = 'FeedApp'
urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'), # build our profile # form to add first name, last name...
    path('myfeed', views.myfeed, name='myfeed'),]

    