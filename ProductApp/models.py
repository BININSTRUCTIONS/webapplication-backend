from django.db import models
from APIs.models import APIInfo

from django.contrib.auth.models import User
from api.models import Customer

# Create your models here.
class CompanyProduct(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(max_length=200, null=True, blank=True)
    date = models.DateField(null=True, blank=True)


class SubscriptionPlan(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=15, null=True, blank=True)
    price = models.FloatField(default=0, null=True, blank=True)
    product = models.ForeignKey(CompanyProduct, on_delete=models.CASCADE)
    term = models.CharField(max_length=1, null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    api_information = models.OneToOneField(APIInfo, on_delete=models.SET_NULL, null=True, blank=True)


class SubscriptionPlanItem(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.CharField(max_length=50)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)


class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    items = models.CharField(max_length=255)
    currency = models.CharField(max_length=4)
    recurrence = models.CharField(max_length=50)
    duration = models.CharField(max_length=100)
    amount = models.BigIntegerField(default=0)


class PaymentNotificationDetail(models.Model):
    id = models.AutoField(primary_key=True)
    information = models.TextField(null=True, blank=True)
