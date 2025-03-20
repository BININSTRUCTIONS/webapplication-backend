from django.shortcuts import render
from rest_framework.response import Response
from django.core.files.storage import FileSystemStorage

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import validate_email

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import *
from django.conf import settings
import json
import os
import us

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Create your views here.
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'business': openapi.Schema(type=openapi.TYPE_STRING)
        },
        required=['business'],
    ),

    response_=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING)
        },
    ),
    
    responses={
        200: 'OK',
        'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING)
                    },
                )
        },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def agent_get(request):
    response = {"status": "failed"}
    business_id = request.data["business"]
    business = Business.objects.get(id=business_id)
    agents = Agent.objects.filter(business=business)
    agent_list = []
    for agent in agents:
        agent_list.append({
            "id": agent.id,
            "business": agent.business.name,
            "firstName": agent.user.first_name,
            "lastName": agent.user.last_name,
            "userName": agent.user.username,
            "email": agent.user.email
        })
    response["agents"] = agent_list
    response["status"] = "ok"
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def assign_user_to_business(request):
    response = {
        "status": "failed"
    }
    data = request.data
    business_id = data["business"]
    email = data["email"]
    password = data["password"]

    print(data)

    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            print(user)
            try:
                business = Business.objects.get(id=business_id)
                print(business)
                business.clients.add(user)
                # business.save()
                response["status"] = "ok"
            except Exception as e:
                print(e)
                response["message"] = "business is not registered"
        else:
            response["message"] = "user who is trying to join is not registered on bininstructions.com. try to sign up."
    except Exception as e:
        print(e)
        response["message"] = "user who is trying to join is not registered on bininstructions.com. try to sign up."

    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def start_chat(request):
    response = {
        "status": "failed",
        "message": ""
    }
    data = request.data
    agent_id = data["agent"]
    business_id = data["business"]
    agent = None
    try:
        agent = Agent.objects.get(id=agent_id)
    except:
        response["message"] = "Agent assigned to the property could not be found."
    
    if agent is not None:
        # print(dir(request.user))
        try:
            business = Business.objects.get(id=business_id)
            print(business)
            if request.user.business_set.contains(business):
                agent.client.add(request.user)
                print(dir(agent))
                # agent.agentclientmessage_set.add(agent=agent, client=request.user)
                response["status"] = "ok"
            else:
                response["message"] = "You are not registered as a client"
        except Exception as e:
            print(e)
            response["message"] = "Business is not registered"
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_chats(request):
    response = {
        "status": "failed"
    }
    data = request.data
    business_id = data["business"]
    try:
        business = Business.objects.get(id=business_id)
        clients = business.clients
        if clients is not None:
            if clients.contains(request.user):
                print(dir(request.user))
                agent_has_client_set = request.user.agenthasclient_set.all()
                print(agent_has_client_set)
                data = []
                if len(agent_has_client_set) != 0:
                    for agent_has_client in agent_has_client_set:
                        data.append({
                            "id": agent_has_client.id,
                            # "agent_id": agent_has_client.agent.id,
                            # "client_id": agent_has_client.client.id,
                            "agent_name": agent_has_client.agent.user.username,
                            "client_name": agent_has_client.client.username
                        })

                response["data"] = data
                response["status"] = "ok"
            else:
                response["message"] = "user is not registered as a client for the business"
    except:
        response["message"] = "Business is not registered"
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_messages(request):
    response = {
        "status": "ok"
    }
    print(request.data)
    data = request.data
    chat_id = data["chat"]
    business = data["business"]

    agent_has_client = AgentHasClient.objects.get(id=chat_id)
    print(agent_has_client.agentclientmessage_set.all())

    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def send_message(request):
    response = {
        "status": "ok"
    }

    data = request.data
    business_id = data["business"]
    chat_id = data["chat"]
    text = data["message"]

    business = None

    try:
        business = Business.objects.get(id=business_id)
        user = None
        authorized = False
        agent = None

        try:
            agent = request.user.agent
            if agent.business == business:
                authorized = True
        except:
            user = request.user
            if user.business_set.contains(business):
                authorized = True

        # print(dir(user))
        if authorized:
            chat = user.agenthasclient_set.filter(id=chat_id)
            if len(chat) == 1:
                chat = chat[0]

                receiver = None
                if agent is not None:
                    receiver = agent.user
                else:
                    receiver = request.user

                message = AgentClientMessage.objects.create(text_content=text, receiver=receiver, agent_has_client=chat)
                chat.agentclientmessage_set.add(message)
                message_set = chat.agentclientmessage_set.all()
                print(dir(chat))
                print(message_set)
    except:
        response["message"] = "Business is not registered"

    return Response(response)




@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def agent_add(request):
    response = {"status": "failed"}
    data = request.data

    first_name = data["firstName"]
    last_name = data["lastName"]
    username = first_name + "_" + last_name
    email = data["email"]
    password = data["password"]
    password_confirmation = data["confirmationPassword"]
    
    assign_role_to_user = None
    try:
        assign_role_to_user = data["assignNewRole"]
    except:
        pass

    try:
        business = Business.objects.get(id=data["business"])
        if password == password_confirmation:
            password = make_password(password)
            try:
                user = User.objects.get(username=username)
                if assign_role_to_user is not None and assign_role_to_user:
                    try:
                        agent = Agent.objects.create(user=user, business=business)  
                        if agent is not None:
                            response["status"] = "ok"
                        else:
                            response["message"] = "couldn't register agent. try again later."
                    except Exception as e:
                        response["message"] = "There is an agent registered with the same information"
                else:
                    response["message"] = "There is a user already registered with the first name and last name provided"
            except:
                try:
                    validate_email(email)
                    try: 
                        user = User.objects.get(email=email)
                        if assign_role_to_user is not None and assign_role_to_user:
                            try:
                                agent = Agent.objects.create(user=user, business=business)  
                                if agent is not None:
                                    response["status"] = "ok"
                                else:
                                    response["message"] = "couldn't register agent. try again later."
                            except Exception as e:
                                response["message"] = "There is a user already registered with the first name and last name provided"
                        else:
                            response["message"] = "There is a user already registered with this email"
                    except:
                        user = User.objects.create(
                            first_name=first_name, 
                            last_name=last_name, 
                            username=username, 
                            email=email,
                            password=password)
                                            
                        agent = Agent.objects.create(user=user, business=business)  
                        if agent is not None:
                            response["status"] = "ok"
                        else:
                            response["message"] = "couldn't register agent. try again later."
                except Exception as e:
                    print(e)
                    response["message"] = "email is not valid. provide a valid email address"
        else:
            response["message"] = "passwords do not match"
    except:
        response["message"] = "Business id is missing. please provide the business ID"
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def assign_agent(request):
    response = {"status": "failed"}
    data = request.data
    agent_id = data["agentID"]
    agent = Agent.objects.get(id=agent_id)

    try:
        house_id = data["houseID"]
        house = House.objects.get(house_id=house_id)
        house.real_estate.agent = agent
    except:
        try:
            land_id = data["landID"]
            land = Land.objects.get(land_id=land_id)
            land.real_estate.agent = agent
        except:
            try:
                building_id = data["buildingID"]
                # house = House.objects.get(house_id=building_id)
                # house.real_estate.agent = agent
            except:
                pass
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def agent_delete(request):
    response = {"status": "failed"}
    agent_id = request.data["agent"]
    agent = Agent.objects.get(id=agent_id)
    agent.delete()
    response["status"] = "ok"
    return Response()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def agent_update(request):
    response = {"status": "failed"}
    data = request.data
    
    agent_id = data["id"]
    agent = Agent.objects.get(id=agent_id)

    print(agent)

    try:
        firstName = data["firstName"]
        agent.user.first_name = firstName
    except:
        pass


    try:
        lastName = data["lastName"]
        agent.user.last_name = lastName
    except:
        pass


    try:
        email = data["email"]
        agent.user.email = email
    except:
        pass


    try:
        password = data["password"]
        agent.user.password = make_password(password)
    except:
        pass

    agent.user.save()
    agent.save()

    response["status"] = "ok"
    return Response(response)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_property_statuses(request):
    response = {"status": "failed"}
    status_list = []
    for status in EstateStatus.objects.all():
        status_list.append(
            {
                "id": status.id,
                "status": status.status
            }
        )
    response["statuses"] = status_list
    response["status"] = "ok"
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def house_get(request):
    response = {"status": "failed"}
    business_id = request.data["business"]
    business = Business.objects.get(id=business_id)
    real_estates = RealEstate.objects.filter(business=business)
    house_list = []
    for real_estate in real_estates:
        house = {
            "id": real_estate.house.house_id,
            "area": real_estate.area,
            "latitude": real_estate.latitude,
            "longitude": real_estate.longitude,
            "address": real_estate.address,
            "price": real_estate.price,
            "state": real_estate.state.name,
            "country": real_estate.country.name,
            "description": real_estate.description,
            "status": real_estate.status.status,
            "number_of_bedrooms": real_estate.house.number_of_bedrooms,
            "number_of_bathrooms": real_estate.house.number_of_bathrooms,
            "number_of_garages": real_estate.house.number_of_garages,
            "number_of_floors": real_estate.house.number_of_floors,
            "media": []
        }
        
        for image in real_estate.propertymedia_set.all():
            house_img = {
                "url": "http://127.0.0.1:8000" + image.media_path.url,
                "is_thumbnail": image.is_thumbnail
            }
            house["media"].append(house_img)

        house_list.append(house)
    response["houseList"] = house_list
    response["status"] = "ok"
    # houses = House.objects.filter(business=business)
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def house_add(request):
    response = {"status": "failed"}
    files = request.FILES

    data = request.data

    business_id = data["businessID"]
    bedRooms = data["bedRoomCount"]
    bathRooms = data["bathRoomCount"]
    garages = data["garageCount"]
    floors = data["floorCount"]
    area = data["area"]
    address = data["address"]
    price = data["price"]
    description = data["description"]
    lat = data["latitude"]
    long = data["longitude"]

    business = Business.objects.get(id=business_id)
    status = EstateStatus.objects.get(id=1)

    country = Country.objects.get(id=data["country"])
    state = State.objects.get(id=data["state"])

    media_files_path = os.path.join(settings.MEDIA_ROOT, "API_MEDIA", "real-estate", business.name)

    realEstate = RealEstate.objects.create(
        area=area,
        latitude=lat,
        longitude=long,
        address=address,
        price=price,
        state=state,
        country=country,
        # agent=agent,
        description=description,
        status=status,
        # available_date=available_date,
        business=business
    )

    if realEstate is not None:
        house = None
        house = House.objects.create(
            number_of_bedrooms=bedRooms,
            number_of_bathrooms=bathRooms,
            number_of_garages=garages,
            number_of_floors=floors,
            real_estate=realEstate
        )

        # file_storage = FileSystemStorage(location=media_files_path)

        for key, file in files.items():
            print(os.path.join(media_files_path, file.name))
            file_path = file.name
            # file_storage.save(file_path, file)
            property_media = PropertyMedia.objects.create(
                media_path=file,
                real_estate=realEstate,
                is_thumbnail=key == "thumbnail"
            )

            # property_media.media_path.name = os.path.join("API_MEDIA", "real-estate", business.name, file.name)
            # property_media.save()
        response["status"] = "ok"
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def house_delete(request):
    response = {"status": "failed"}
    business_id = request.data["businessID"]
    house_ids = request.data["ids"]

    for id in house_ids:
        house = House.objects.get(house_id=id)
        real_estate = house.real_estate

        house = Business.objects.get(id=business_id).realestate_set.filter(house=house_ids[0])
        house.delete()
        response["status"] = "ok"
    return Response()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def house_update(request):
    response = {"status": "failed"}
    data = request.data
    house = House.objects.get(house_id=data["houseID"])
    real_estate = house.real_estate

    try:
        real_estate.area = data["area"]
    except:
        pass

    try:
        real_estate.latitude = data["latitude"]
    except:
        pass

    try:
        real_estate.longitude = data["longitude"]
    except:
        pass

    try:
        real_estate.address = data["address"]
    except:
        pass

    try:
        real_estate.price = data["price"]
    except:
        pass

    try:
        real_estate.country = data["country"]
    except:
        pass

    try:
        real_estate.state = data["state"]
    except:
        pass

    try:
        real_estate.agent = data["agent"]
    except:
        pass

    try:
        real_estate.description = data["description"]
    except:
        pass

    try:
        real_estate.status = data["status"]
    except:
        pass

    try:
        real_estate.available_date = data["available_date"]
    except:
        pass

    try:
        real_estate.business = Business.objects.get(data["business"])
    except:
        pass

    real_estate.save()

    try:
        house.number_of_bedrooms = data["bedRoomCount"]
    except:
        pass

    try:
        house.number_of_bathrooms = data["bathRoomCount"]
    except:
        pass

    try:
        house.number_of_garages = data["garageCount"]
    except:
        pass

    try:
        house.number_of_floors = data["floorCount"]
    except:
        pass

    house.save()

    response["status"] = "ok"


    return Response(response)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def land_get(request):
    response = {"status": "failed"}
    business_id = request.data["business"]
    business = Business.objects.get(id=business_id)
    agents = Land.objects.filter(business=business)
    return Response()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def land_add(request):
    response = {"status": "failed"}
    data = request.data

    area = data["area"]
    latitude = data["latitude"]
    longitude = data["longitude"]
    address = data["address"]
    price = data["price"]

    try:
        country = Country.objects.get(id=data["country"])
        state = State.objects.gete(id=data["state"])
    except:
        response["message"] = "Invalid country or state is provided. aborting registering process."

    # agent = data["agent"]

    description = data["description"]

    try:
        status = EstateStatus.objects.get(id=data["status"])
    except:
        response["message"] = "Invalid state is provided. aborting registering process."
    available_date = data["available_date"]
    
    try:
        business = Business.objects.get(id=data["business"])
    except:
        response["message"] = "Invalid business id is provided. aborting registering process."

    real_estate = RealEstate.objects.create(
        area=area,
        latitude=latitude,
        longitude=longitude,
        address=address,
        price=price,
        country=country,
        state=state,
        # agent=agent,
        description=description,
        status=status,
        available_date=available_date,
        business=business
    )

    if real_estate is not None:
        land = Land.objects.create(real_estate=real_estate)
        if land is not None:
            response["status"] = "ok"
        else:
            real_estate.delete()
            response["message"] = "Error occurred when registering property"
    else:
        response["message"] = "Error occurred when registering property"
    
    if response["message"] != "":
        response["status"] = "ok"
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def land_delete(request):
    response = {"status": "failed"}
    land_id = request.data["land"]
    land = Land.objects.get(land_id=land_id)
    land.delete()
    return Response()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def land_update(request):
    response = {"status": "failed"}
    data = request.data
    land = Land.objects.get(land_id=data["houseID"])
    real_estate = land.real_estate

    try:
        real_estate.area = data["area"]
    except:
        pass

    try:
        real_estate.latitude = data["latitude"]
    except:
        pass

    try:
        real_estate.longitude = data["longitude"]
    except:
        pass

    try:
        real_estate.address = data["address"]
    except:
        pass

    try:
        real_estate.price = data["price"]
    except:
        pass

    try:
        real_estate.country = data["country"]
    except:
        pass

    try:
        real_estate.state = data["state"]
    except:
        pass

    try:
        real_estate.agent = data["agent"]
    except:
        pass

    try:
        real_estate.description = data["description"]
    except:
        pass

    try:
        real_estate.status = data["status"]
    except:
        pass

    try:
        real_estate.available_date = data["available_date"]
    except:
        pass

    try:
        real_estate.business = data["business"]
    except:
        pass

    real_estate.save()
    return Response()



@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_countries(request):
    response = {"status": "failed"}
    countries = []
    for country in Country.objects.all():
        countries.append({
            "id": country.id,
            "name": country.name
        })

    response["status"] = "ok"

    response["countries"] = countries
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_states(request):
    response = {"status": "failed"}
    states = []
    country = Country.objects.get(id=request.data["country"])
    if country is not None:
        for state in State.objects.filter(country=country):
            states.append({
                "id": state.id,
                "name": state.name
            })
    else:
        response["message"] = "country is invalid"

    response["status"] = "ok"
    response["states"] = states
    return Response(response)

