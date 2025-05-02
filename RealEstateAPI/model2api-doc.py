file = open(r"E:\Rukshan\bininstructions\webapplication\backend\RealEstateAPI\models.py", "r+")

current_class = None

model_data = {}

api_base_url = "http://127.0.0.1:8000/api/v1/"

for line in file.readlines():
    if line.startswith("class"):
        class_name = line.split(" ")[1].split("(")[0]
        model_data[class_name] = []
        current_class = class_name.strip()
        # print("Class name: ", class_name)
    else:
        if line.__contains__("="):
            field_name = line.split("=")[0].strip()
            field_type = line.split("=")[1].split("models.")[1].split("(")[0]
            # print("\t\t", field_name, field_type)
            if field_type == "ForeignKey":
                related_model = line.split("=")[1].split("models.")[1].split("(")[1].split(",")[0]
                if model_data.keys().__contains__(related_model):
                    primary_key_field = ""
                    for field in model_data[related_model]:
                        if primary_key_field == "":
                            if field.__contains__(" [primary key]"):
                                print(field)
                                id = field.split(" [primary key]")[0]
                                print("\t\t", id)
                    if primary_key_field == "":
                        primary_key_field == "id"
                    field_name += "_id"
                # print("\t\t\t", related_model)
            elif field_type == "AutoField":
                args = line.split("=")[1].split("models.")[1].split("(")[1].split(",")
                # print(args)
                if args.__contains__("primary_key"):
                    value = line.split("models.")[1].split("(")[1].split("primary_key")
                    # print(value)
                    if len(value) > 0:
                        # print(value)
                        if value[1] != '':
                            value = value[1].split("=")[1]
                            # print(value)
                            if value.startswith("True"):
                                field_name += " [primary key]"
                            elif value.startswith("False"):
                                pass
            model_data[current_class].append(field_name)

# print(model_data)
for key, value in model_data.items():
    print(key, value)


def prepare_add_api_endpoint(model_data):
    for model, data in model_data.items():
        api_endpoint = api_base_url + model.lower() + "/add"
        api_response = "{"
        for property in data:
            if not property.__contains__(" [primary key]"):
                api_response += "\t"+ property + ": ,\n"
        api_response.removesuffix(",")
        api_response += "}"
        print(api_endpoint)
        print(api_response)
        print()


def prepare_get_api_endpoint(model_data):
    for model, data in model_data.items():
        api_endpoint = api_base_url + model.lower() + "/add"
        api_response = "{"
        for property in data:
            if not property.__contains__(" [primary key]"):
                api_response += "\t"+ property + ": ,\n"
        api_response.removesuffix(",")
        api_response += "}"
        print(api_endpoint)
        print(api_response)
        print()


def prepare_update_api_endpoint(model_data):
    for model, data in model_data.items():
        api_endpoint = api_base_url + model.lower() + "/add"
        api_response = "{"
        found_primary_key = False
        for property in data:
            if not found_primary_key:
                if property.__contains__(" [primary key]"):
                    found_primary_key = True
                    api_response += "\t"+ property + ": ,\n"
            else:
                pass
        api_response.removesuffix(",")
        api_response += "}"
        print(api_endpoint)
        print(api_response)
        print()


prepare_add_api_endpoint(model_data)