from django.db import models

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