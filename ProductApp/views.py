from django.shortcuts import render
from django.http.response import FileResponse, JsonResponse, HttpResponse
import os
from datetime import datetime


from api.models import ProductOrder

# Create your views here.
def download_file(request):
    # response = FileResponse(open(os.getcwd().replace("\\", '/') + "/products/RCCG/2024-08-17/y2mate.com - Adele  Set Fire To The Rain Live at The Royal Albert Hall_1080p_9TeBEjL.mp4", "rb"), as_attachment=True)
    # print(request.GET)

    order = ProductOrder.objects.filter(id=request.GET["oid"])
    product = order[0].product

    if order[0].last_download_time is None:
        product_name = product.application_name
        path_for_application = os.getcwd().replace("\\", '/') + f"/products/{product_name}"

        product_launch_date_list = os.listdir(path_for_application)
        
        latest_date = None
        for date in product_launch_date_list:
            current_date = date
            if latest_date is None:
                latest_date = current_date
            else:
                if latest_date < current_date:
                    latest_date = current_date

        path_for_application += f"/{str(latest_date)}/standalone"

        file = os.listdir(path_for_application)[0]

        path_for_application += f"/{file}"
        print(path_for_application)
        # order.update(last_download_time=datetime.now())
        file = open(path_for_application, "rb")
        response = FileResponse(file, as_attachment=True)
        response.set_headers(file)
        # response = JsonResponse({"application_name": path_for_application, "date": str(latest_date)})
    else:
        response = HttpResponse("<h1>404 Not found.</h1>")

    return response


def activate_key_manager_plan(request):
    response = {"status": "failed"}
    data = request.data
    try:
        plan_id = data["plan"]
    except:
        pass
