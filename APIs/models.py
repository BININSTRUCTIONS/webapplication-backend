from django.db import models
from django.contrib.auth.models import User

from api.models import Customer, CustomersHavePlans

# Create your models here.
# class Message(models.Model):
#     message = models.TextField()
#     sent_time = models.DateTimeField()
#     media = models.FileField()
#     sender = models.ForeignKey()
#     receiver = models.ForeignKey()


class APIInfo(models.Model):
    id = models.AutoField(primary_key=True)
    calls_per_minute = models.IntegerField(default=12)


class APIKey(models.Model):
    id = models.AutoField(primary_key=True)
    api_key = models.CharField(max_length=255)
    last_used = models.DateTimeField(null=True, blank=True)
    remaining_requests = models.IntegerField(null=True, blank=True)
    requests_made = models.IntegerField(null=True, blank=True)
    customers_have_plans = models.ForeignKey(CustomersHavePlans, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
