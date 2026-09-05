from django.db import models

# Create your models here.
class Images(models.Model):
    photo = models.ImageField(upload_to='photo/',verbose_name=u'图片地址')

    def __str__(self):
        return self.photo.name