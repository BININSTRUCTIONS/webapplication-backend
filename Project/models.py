from django.db import models

# Create your models here.
class Stage(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)


class ProcessStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20)


class Process(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    status = models.ForeignKey(ProcessStatus, on_delete=models.DO_NOTHING, null=True)


class SubProcess(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    status = models.ForeignKey(ProcessStatus, on_delete=models.DO_NOTHING, null=True)
    parentProcess = models.ForeignKey(Process, on_delete=models.CASCADE)