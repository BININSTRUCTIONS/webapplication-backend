from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DigitalKey(models.Model):
    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=256)
    max_activations = models.IntegerField(default=1)
    current_activations = models.IntegerField(default=0, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
