"""
    用户相关的路径
"""
from django.urls import path

from user.views import user_register, user_login, user_logout
import user.views

urlpatterns = [
    path('register', user_register, name='register'),
    path('login', user_login, name='login'),
    path('logout', user_logout, name='logout'),
    path("lishi", user.views.lishi, name="lishi"),
    path("diangu", user.views.diangu, name="diangu"),
    path("fengbei", user.views.fengbei, name="fengbei"),
    path("jianshen", user.views.jianshen, name="jianshen"),
    path("qunxing", user.views.qunxing, name="qunxing"),
    path("yangsheng", user.views.yangsheng, name="yangsheng"),
    path("yiyinyishan", user.views.yiyinyishan, name="yiyinyishan"),
    path("yizhu", user.views.yizhu, name="yizhu"),
]

