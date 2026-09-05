"""
    predict相关的路径
"""
from django.urls import path
from .views import *
urlpatterns = [
    path('chatindex', chatindex, name='chatindex'),
    path('add', add, name='add')
]