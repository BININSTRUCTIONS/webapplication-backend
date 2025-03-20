from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class AnonymousUser(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField()
    code = models.CharField(max_length=255, null=True, blank=True)


class CustomerServiceAgent(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clients = models.ManyToManyField(AnonymousUser, through='CustomerServiceChat')
    users = models.ManyToManyField(User, through='CustomerServiceChat', related_name="registered_user")


class CustomerServiceChat(models.Model):
    id = models.AutoField(primary_key=True)
    customer_service_agent = models.ForeignKey(CustomerServiceAgent, on_delete=models.CASCADE, null=True, blank=True)
    anonymous_user = models.ForeignKey(AnonymousUser, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class CustomerServiceMessage(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(max_length=1024, default="")
    media = models.FileField(null=True, blank=True, upload_to="customer-service-chat/")
    datetime = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True) # customer service agent and admin
    customer_service_chat = models.ForeignKey(CustomerServiceChat, on_delete=models.DO_NOTHING, null=True, blank=True)