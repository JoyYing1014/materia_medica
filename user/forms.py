import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form
from django.forms.models import ModelForm

from user.models import UserProfile


# 写法一、继承From的写法
# class UserRegisterForm(Form):
#     username = forms.CharField(max_length=50, min_length=6, error_messages={'min_lengh': "用户名至少6位"}, label="用户名")
#     email = forms.EmailField(required=True, error_messages={'required': "必须填写邮箱信息"}, label='邮箱')
#     mobile = forms.CharField(required=True, error_messages={'required': "必须填写手机号"}, label='手机号')
#     # widget=forms.widgets.PasswordInput 输入框为密码格式
#     password = forms.CharField(required=True, error_messages={'required': "必须填写密码"}, label='密码',
#                                widget=forms.widgets.PasswordInput)
#
#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         # username 正则匹配
#         result = re.match(r'[a-zA-Z]\w{5,}', username)
#         if not result:
#             raise ValidationError('用户名必须字母开头')
#         return username


# 写法二、这里是继承modelForm的写法，继承modelForm可以获取到model里面所有的值
class RegisterForm(ModelForm):
    """
        注册表单
    """

    class Meta:
        # 获取到模型里面的属性
        model = UserProfile
        # fields = '__all__’ 即获取所有属性
        # exclude = ['username','email'] 即排除这些字段
        fields = ['username', 'email', 'mobile', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # username 正则匹配
        result = re.match(r'[a-zA-Z]\w{5,}', username)
        if not result:
            raise ValidationError('用户名必须字母开头')
        return username


class LoginForm(Form):
    """
        登录表单
    """
    username = forms.CharField(max_length=50, min_length=6, error_messages={'min_lengh': "用户名至少6位"},
                               label="用户名")
    password = forms.CharField(required=True, error_messages={'required': "必须填写密码"}, label='密码',
                               widget=forms.widgets.PasswordInput)

    def clean_username(self):
        # 拿到表单里面的用户名
        username = self.cleaned_data.get('username')
        # 校验数据库里面这个用户名是否存在，不存在就抛出异常
        if not UserProfile.objects.filter(username=username).exists():
            raise ValidationError('用户名不存在')
        return username

