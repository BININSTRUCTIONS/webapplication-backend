from django.db import models

# Create your models here.
class AnonymousUser(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField()
    code = models.CharField(max_length=255, null=True, blank=True)


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(max_length=1024, default="")
    media = models.FileField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    project_discussion = models.ForeignKey(
        ProjectDiscussion, on_delete=models.CASCADE, null=True, blank=True
    )
