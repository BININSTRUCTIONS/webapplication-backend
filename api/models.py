from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
import os



# from CustomerService.models import AnonymousUser


product_storage = FileSystemStorage(location=f"{os.getcwd()}/products", base_url=None)

def upload_standalone_application(instance, filename):
    # print("received file name: (standalone)", filename, "\n\n")
    # print(os.getcwd())
    print("#################")
    print(instance.application_name)
    print("#################")
    return f"{filename}"

def upload_dependencies(instance, filename):
    # print("received file name: (dependencies)", filename, "\n\n")
    return f"{filename}"


class ApplicationType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=15)


class PricePlan(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    one_time_payment = models.FloatField(null=True, blank=True)
    recurring_payment = models.FloatField(null=True, blank=True)
    term_name = models.CharField(max_length=100, null=True, blank=True)
    application_type = models.ForeignKey(ApplicationType, on_delete=models.CASCADE, null=True, blank=True)


class ProjectStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20)


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    plan = models.ForeignKey(PricePlan, on_delete=models.DO_NOTHING, null=True, blank=True)


class Designation(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE, null=True, blank=True)
    password_reset_code = models.IntegerField(null=True, blank=True)
    


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    proposal = models.FileField(null=True, blank=True, default=None)
    proposal_link = models.CharField(
        max_length=256, null=True, blank=True, default=None
    )
    design_files = models.FileField(null=True, blank=True, default=None)
    design_link = models.CharField(max_length=256, null=True, blank=True, default=None)
    srs = models.FileField(null=True, blank=True, default=None)
    type = models.ForeignKey(ApplicationType, on_delete=models.DO_NOTHING, default=None)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=None)
    status = models.ForeignKey(ProjectStatus, on_delete=models.DO_NOTHING, default=None)
    start_date = models.DateField(null=True, blank=True, default=None)
    end_date = models.DateField(null=True, blank=True, default=None)
    advanced_payment_state = models.BooleanField(default=False)
    one_time_payment_status = models.BooleanField(default=False)
    payment_link = models.CharField(max_length=255, null=True, blank=True)
    frontend_progress = models.IntegerField(default=0)
    backend_progress = models.IntegerField(default=0)
    database_progress = models.IntegerField(default=0)
    # employees = models.ManyToManyField(Employee, null=True, blank=True)


class PaymentHistory(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    amount = models.FloatField()
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING)


class ProjectHasEmployees(models.Model):
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class AccountType(models.Model):
    type = models.CharField(max_length=15)


#   Tables for chat system
class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    profile_url = models.CharField(max_length=1024, default="", blank=True)
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE, null=True)
    password_reset_code = models.CharField(max_length=6, null=True, blank=True)
    subscription_plans = models.ManyToManyField("ProductApp.SubscriptionPlan", through="CustomersHavePlans")
    subscribed_to_newsletter = models.BooleanField(default=False)


class SecurityQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=50)
    answer = models.CharField(max_length=20)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, null=True, blank=True)


class CustomersHavePlans(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    plan = models.ForeignKey("ProductApp.SubscriptionPlan", on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey("ProductApp.CompanyProduct", on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField()


# class APIKey(models.Model):
#     id = models.AutoField(primary_key=True)
#     api_key = models.CharField(max_length=255)
#     last_used = models.DateTimeField(null=True, blank=True)
#     remaining_requests = models.IntegerField(null=True, blank=True)
#     requests_made = models.IntegerField(null=True, blank=True)
#     customers_have_plans = models.ForeignKey(CustomersHavePlans, on_delete=models.CASCADE, null=True, blank=True)
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
#     product = models.ForeignKey(CompanyProduct, on_delete=models.CASCADE, null=True, blank=True)
#     renew_frequency = models.CharField(max_length=2, null=True, blank=True)
#     renew_times = models.IntegerField(null=True, blank=True)


class ProjectDiscussion(models.Model):
    id = models.AutoField(primary_key=True)
    involved_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    involved_staff = models.ManyToManyField(User, through="ProjectDiscussionHasStaff")
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(max_length=1024, default="")
    media = models.FileField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True) # sender of the message
    project_discussion = models.ForeignKey(ProjectDiscussion, on_delete=models.CASCADE, null=True, blank=True)
    is_seen = models.BooleanField(default=False)


class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.DO_NOTHING, null=True, blank=True
    )


class ProjectManager(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.DO_NOTHING, null=True, blank=True
    )


class ProjectDiscussionHasStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    project_discussion = models.ForeignKey(
        ProjectDiscussion, on_delete=models.CASCADE
    )


class Product(models.Model):
    application_name = models.CharField(max_length=100)
    price = models.FloatField(default=0.0)
    description = models.TextField(default="")
    standalone_application = models.FileField() # exe setup file
    dependencies = models.FileField()           # zip file with compiled dependencies
    standalone_application_path = models.CharField(max_length=1024, null=True, blank=True)
    dependency_path = models.CharField(max_length=1024, null=True, blank=True)


class ProductMedia(models.Model):
    id = models.AutoField(primary_key=True)
    media_file = models.FileField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)



class PaymentStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=15)


class ProductOrder(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)
    payment_status = models.ForeignKey(PaymentStatus, on_delete=models.CASCADE)
    last_download_time = models.DateTimeField(null=True, blank=True)


class LicenseKey(models.Model):
    id = models.AutoField(primary_key=True)
    license_key = models.CharField(max_length=500)
    is_active = models.BooleanField(default=False)
    activated_date = models.DateTimeField(null=True, blank=True)
    order = models.OneToOneField(ProductOrder, on_delete=models.CASCADE)


class Plan(models.Model):
    plan_name = models.CharField(max_length=45)
    price = models.FloatField(null=True)
    users = models.ManyToManyField(User)


class API(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25, null=True, blank=True)
    # max_calls_per_minute = models.IntegerField(null=True, blank=True)
    product = models.OneToOneField("ProductApp.CompanyProduct", on_delete=models.CASCADE)
    customer = models.ManyToManyField(Customer, through='CustomerHasAPI')


class CustomerHasAPI(models.Model):
    id = models.AutoField(primary_key=True)
    api = models.ForeignKey(API, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    number_of_calls = models.IntegerField(default=0)



class PasswordResetRequestEmailList(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField()
    code = models.CharField(max_length=6, null=True, blank=True)


class NewsletterSubscription(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField()



class PaymentReceipt(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    captured_amount = models.CharField(max_length=100, null=True, blank=True)
    payhere_amount = models.CharField(max_length=100, null=True, blank=True)
    status_message = models.CharField(max_length=100, null=True, blank=True)
    status_code = models.CharField(max_length=1, null=True, blank=True)
    method = models.CharField(max_length=100, null=True, blank=True)
    message_type = models.CharField(max_length=100, null=True, blank=True)
    subscription_id = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    items = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=100, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    amount = models.CharField(max_length=100, null=True, blank=True)
    date_of_payment = models.DateField(null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)



class Review(models.Model):
    id = models.AutoField(primary_key=True)
    userName = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    review = models.TextField(null=True, blank=True)
