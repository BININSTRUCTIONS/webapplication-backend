from typing import Any
from APIs.models import APIKey

from rest_framework.response import Response

from django.template.response import TemplateResponse


class APIAuthenticationMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response


    def __call__(self, request):
        json_response = {"message": ""}
        response = self.get_response(request)
        # if hasattr(response, 'render') and callable(response.render):
        #     response.render()

        if isinstance(response, TemplateResponse):
            # print("Template Response")
            response.render()
            
        # auth_header = request.headers.get("Authorization")
        # if auth_header:
        #     try:
        #         token = auth_header.split(' ')[1]
        #         api_key = APIKey.objects.get(api_key=token)
        #         api_key.requests_made += 1
        #         api_key.remaining_requests -= 1
        #         api_key.save()
        #         request.user = api_key.user
        #     except APIKey.DoesNotExist:
        #         json_response["message"] = "Invalid API key"
                # print(response.data)
                
                # return Response(json_response)
        
        return response
