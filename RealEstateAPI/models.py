from django.db import models
from django.contrib.auth.models import User
from InventoryManagementAPIApp.models import Business



"""
@property user > 
@property business >
"""
class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True)
    client = models.ManyToManyField(User, through="AgentHasClient", related_name="client")


class AgentHasClient(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.DO_NOTHING)
    client = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    # message = models.ForeignKey(AgentClientMessage, on_delete=models.DO_NOTHING, null=True)


class AgentClientMessage(models.Model):
    text_content = models.TextField(max_length=500)
    media = models.FileField()
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    agent_has_client = models.ForeignKey(AgentHasClient, on_delete=models.CASCADE, null=True)


"""
@property name >
"""
class Country(models.Model):
    name = models.CharField(max_length=50)

"""
@property name >
@property country >
"""
class State(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

"""
@property name > 
@property state > 
"""
class City(models.Model):
    name = models.CharField(max_length=50)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

"""
@property id > 
@property status > 
"""
class EstateStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20)

"""
@property area > 
@property latitude > 
@property longitude > 
@property address > 
@property price > 
@property country > 
@property state > 
@property agent > 
@property description > 
@property status > 
@property available_date > 
@property business > 
"""
class RealEstate(models.Model):
    area = models.FloatField()
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    address = models.CharField(max_length=200, null=True)
    price = models.FloatField(default=0.0)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    agent = models.ForeignKey(Agent, on_delete=models.DO_NOTHING, null=True)
    description = models.TextField(null=True, blank=True)
    status = models.ForeignKey(EstateStatus, on_delete=models.CASCADE, null=True, blank=True)
    available_date = models.DateField(null=True, blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True)

"""
@property land_id > 
@property real_estate > 
"""
class Land(models.Model):
    land_id = models.AutoField(primary_key=True)
    real_estate = models.ForeignKey(RealEstate, on_delete=models.CASCADE)

"""
@property house_id > 
@property number_of_bedrooms > 
@property number_of_bathrooms > 
@property number_of_garages > 
@property number_of_floors > 
@property real_estate > 
"""
class House(models.Model):
    house_id = models.AutoField(primary_key=True)
    number_of_bedrooms = models.IntegerField(default=1)
    number_of_bathrooms = models.IntegerField(default=1)
    number_of_garages = models.IntegerField(default=1)
    number_of_floors = models.IntegerField(default=1)
    real_estate = models.OneToOneField(RealEstate, on_delete=models.CASCADE)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    
    return "API_MEDIA/real-estate/{0}/{1}".format(instance.real_estate.business.name, filename)

"""
@property media_id > 
@property media_path > 
@property real_estate > 
@property is_thumbnail > 
"""
class PropertyMedia(models.Model):
    media_id = models.AutoField(primary_key=True)
    media_path = models.FileField(upload_to=user_directory_path)
    real_estate = models.ForeignKey(RealEstate, on_delete=models.CASCADE)
    is_thumbnail = models.BooleanField()




