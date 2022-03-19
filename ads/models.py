from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    """ Default Django User model """
    
    def __str__(self):
        return self.username


class MainCategory(models.Model):
    """
    Ad main category model, 
    url_name is the name of the category in the url when clicked 
    """
    category = models.CharField(max_length=50, unique=True)
    url_name = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return f'{self.category}, url /{self.url_name}'


class SubCategory(models.Model):
    """ Each sub category model that belongs to a main category """
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE)
    subcategory = models.CharField(max_length=50)

    def __str__(self):
        return f'Subcategoria {self.subcategory} de {self.main_category.category}'


class Advertisement(models.Model):
    """ Each ad model webscrapped from the page site """
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, null=True)
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.title}. Precio: {self.price}€'