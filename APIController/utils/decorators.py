from functools import wraps
from django.http import JsonResponse

from APIs.models import APIKey

from datetime import datetime

from django.utils import timezone


def key_manager_api_authentication(view_function):
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        json_response = {}
        # print(request.headers)
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
                api_key = APIKey.objects.get(api_key=token)

                last_used_time = api_key.last_used

                current_time = timezone.now()
                difference_in_minutes = 1
                if last_used_time != None:
                    time_difference = current_time - last_used_time
                    difference_in_minutes = int(time_difference.total_seconds()) / 60

                limited_calls = api_key.customers_have_plans.plan.api_information.calls_per_minute

                if difference_in_minutes < 1:
                    if api_key.requests_made == limited_calls:
                        return JsonResponse({"message": "Maximum number of calls per minute reached."})
                    else:
                        api_key.remaining_requests = api_key.remaining_requests - 1
                        api_key.requests_made = api_key.requests_made + 1
                        api_key.last_used = timezone.now()
                        api_key.save()
                else:
                    api_key.requests_made = 1
                    api_key.remaining_requests = limited_calls - 1
                    api_key.last_used = timezone.now()
                    api_key.save()

                request.user = api_key.customers_have_plans.customer.user
                return view_function(request, *args, **kwargs)
            except APIKey.DoesNotExist as e:
                # print(e)
                json_response["message"] = "Invalid API key"
                return JsonResponse(json_response)
    return wrapper
