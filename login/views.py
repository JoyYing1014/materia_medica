from django.shortcuts import render,HttpResponse,redirect
from django.views import View
import os
from django.conf import settings
import torch
from torchvision import transforms
from PIL import Image
# Create your views here.

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # 检查用户名和密码是否匹配
        if username == 'admin' and password == 'password':
            return render(request,'success.html',{'username':username})
        else:
            return render(request,'login.html',{'error':'Invalid username or password'})
    return render(request,'login.html')