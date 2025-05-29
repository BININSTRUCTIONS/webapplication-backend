from django.db import models
from APIs.models import APIInfo

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


class PaymentNotificationDetail(models.Model):
    id = models.AutoField(primary_key=True)
    information = models.TextField(null=True, blank=True)
