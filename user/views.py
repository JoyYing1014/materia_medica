from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from user.forms import RegisterForm, LoginForm
from user.models import UserProfile

"""
    视图函数
"""


def index(request):
    """
    返回首页
    :param request:
    :return:
    """
    return render(request, "index.html")


def case_study(request):
    """Render the standalone product case-study landing page."""
    return render(request, "case_study.html")


def user_register(request):
    """
    用户注册
    :param request:
    :return:
    """
    if request.method == 'GET':  # 注意get一定要大写，不然无法将表单渲染在页面上
        return render(request, 'user/register.html')
    else:
        rform = RegisterForm(request.POST)  # 使用form获取数据
        # print('--------》', rform)
        print("errors", rform.errors)
        if rform.is_valid():  # 进行数据的校验
            # 从干净的数据中取值，即通过前端校验的数据
            username = rform.cleaned_data.get('username')
            email = rform.cleaned_data.get('email')
            mobile = rform.cleaned_data.get('mobile')
            password = rform.cleaned_data.get('password')
            # 如果用户名/手机号不存在的话，才进行添加数据操作
            if not UserProfile.objects.filter(Q(username=username) | Q(mobile=mobile)).exists():
                # 注册到数据库中
                password = make_password(password)  # 密码进行加密
                user = UserProfile.objects.create(username=username, password=password, email=email, mobile=mobile)
                if user:
                    # 如果用户创建成功，则提示注册成功
                    return HttpResponse('注册成功')
            else:
                # 否则用户名/手机号已存在
                return render(request, 'user/register.html', context={'msg': '用户名或者手机号已经存在！'})
        # 数据校验失败，就提示注册失败
        return render(request, 'user/register.html', context={'msg': '用户名或者手机号已经存在，请重新填写！'})


def user_login(request):
    """
    用户登陆
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'user/login.html')
    else:
        lform = LoginForm(request.POST)
        print('--------》', lform)
        print("errors", lform.errors)
        if lform.is_valid():
            username = lform.cleaned_data.get('username')
            password = lform.cleaned_data.get('password')
            # 查询数据库,如果加密后的两个密码一致的话登录成功
            user = UserProfile.objects.filter(username=username).first()
            flag = check_password(password, user.password)
            if flag:
                # 登陆成功后，保存session信息，并进入首页
                # session信息会保存到django_session表中，并进行base64加密
                request.session['username'] = username
                return redirect(reverse('index'))
        return render(request, 'user/login.html', context={'errors': lform.errors})


def user_logout(request):
    """
    用户注销
    :param request:
    :return:
    """
    # 方法一、可自行清空session，再重定向到首页
    # request.session.clear() # 仅删除字典
    # 用户注销后，把session给清空，并且重定向回首页
    # request.session.flush()  # 删除django_session +cookie + 字典
    # return redirect(reverse('index'))

    # 方法二、若model类继承了AbstractUser，可直接使用系统自带的退出登录，即logout；不需要自己去清空session
    logout(request)
    return redirect(reverse('index'))

def lishi(request):
    return render(request, "lishi.html")
def diangu(request):
    return render(request, "diangu.html")

def fengbei(request):
    return render(request, "fengbei.html")

def jianshen(request):
    return render(request, "jianshen.html")

def qunxing(request):
    return render(request, "qunxing.html")

def yangsheng(request):
    return render(request, "yangsheng.html")

def yiyinyishan(request):
    return render(request, "yiyinyishan.html")

def yizhu(request):
    return render(request, "yizhu.html")
