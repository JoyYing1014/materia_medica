from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

"""
    数据库模型类
"""


#  继承AbstractUser，可以使用他本身的登录/退出登录方法；
#  同时也可以继承auth_user本身的所有数据库字段
class UserProfile(AbstractUser):
    # 这里我们设置mobile为唯一，之后方便用于登录校验
    mobile = models.CharField(max_length=11, verbose_name="手机号", unique=True)
    # icon的图片我们指定生成到media文件夹里，并且记得去settings里面进行配置
    # media创建在static同级目录下
    # upload_to表示文件上传的路径，uploads/%Y/%m/%d：他会在media文件底下依次创建2019--05--文件名
    icon = models.ImageField(upload_to='uploads/%Y/%m/%d')

    class Meta:
        db_table = 'userprofile'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name

