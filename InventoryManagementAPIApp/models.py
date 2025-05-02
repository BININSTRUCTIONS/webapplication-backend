from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Manufacturer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

class MeasurementUnit(models.Model):
    id = models.AutoField(primary_key=True)
    unit = models.CharField(max_length=10)

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date = models.DateTimeField(null=True)

class UserType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100)

class ProductType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50)


class ProductMedia(models.Model):
    image = models.FileField(null=True)


class Aisle(models.Model):
    number = models.IntegerField()


class Product(models.Model):
    name = models.CharField(max_length=100)
    image_path = models.CharField(max_length=255)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, null=True)
    measurement_unit = models.ForeignKey(MeasurementUnit, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    manufacturer = models.ManyToManyField(Manufacturer)
    stock = models.ManyToManyField(Stock, through="ProductHasStock")


class ProductHasStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True)
    price = models.FloatField()
    remains = models.IntegerField()
    total_qty = models.IntegerField()
    image_path = models.ForeignKey(ProductMedia, on_delete=models.DO_NOTHING, null=True)
    measurement_unit_quantity = models.FloatField()
    has_discount = models.BooleanField(default=False)
    discount = models.FloatField()
    aisles = models.ManyToManyField(Aisle)


class BusinessType(models.Model):
    type = models.CharField(max_length=50)


class Business(models.Model):
    name = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    type = models.ForeignKey(BusinessType, on_delete=models.CASCADE, null=True)
    clients = models.ManyToManyField(User, related_name="BusinessHasClient")

