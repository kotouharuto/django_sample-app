from django.db import models

# Create your models here.
class Post(models.Model):
 category = models.CharField('category', max_length=15)
 budget = models.IntegerField('budget')
 def __str__(self):
  return self.category
 def __int__(self):
  return self.budget

class Ikea(models.Model):
 item_id = models.IntegerField('item_id')
 name = models.CharField('name', max_length=100)
 category = models.CharField('category', max_length=100)
 price = models.FloatField('price', max_length=100)
 old_price = models.CharField('old_price', max_length=100)
 sellable_online = models.BooleanField('sellable_online', max_length=10)
 link = models.URLField('link', max_length=200)
 other_colors = models.CharField('other_colors', max_length=10)
 short_description = models.CharField('short_description', max_length=200)
 designer = models.CharField('designer', max_length=100)
 depth = models.IntegerField('depth')
 height = models.IntegerField('height')
 width = models.IntegerField('width')