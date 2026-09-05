"""
    predict相关的路径
"""
from django.urls import path
from predict.views import predictindex
urlpatterns = [
    path('predictindex', predictindex, name='predictindex'),

]