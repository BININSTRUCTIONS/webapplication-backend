from django.db import models


class Party(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=20)

class CollaborationProduct(models.Model):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=50)
    parties = models.ManyToManyField(Party, through="CollaborationProductHasParty")


class ProductPlan(models.Model):
    id = models.AutoField(primary_key=True)
    planName = models.CharField(max_length=50)
    price = models.FloatField(default=0.0)
    available = models.BooleanField(default=True)
    isExclusive = models.BooleanField(default=False)
    product = models.ForeignKey(CollaborationProduct, on_delete=models.CASCADE)


class CollaborationProductHasParty(models.Model):
    id = models.AutoField(primary_key=True)
    collaboration_product = models.ForeignKey(CollaborationProduct, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)


class WaitingUser(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    whatsapp = models.CharField(max_length=12)
    website = models.CharField(max_length=255)
    email = models.EmailField()
    brandName = models.CharField(max_length=255, null=True, blank=True)
    jobTitle = models.CharField(max_length=255, null=True, blank=True)
    payedUpfront = models.BooleanField(default=False)
    product = models.ManyToManyField(CollaborationProduct, through="WaitingUserHasProduct")


class WaitingUserHasProduct(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(CollaborationProduct, on_delete=models.CASCADE)
    waiting_user = models.ForeignKey(WaitingUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(ProductPlan, on_delete=models.CASCADE)


class CollaborationProductMessage(models.Model):
    id = models.AutoField(primary_key=True)
    fullName = models.CharField(max_length=100)
    email = models.EmailField()
    companyBrand = models.CharField(max_length=255)
    useCase = models.CharField(max_length=255)
    message = models.TextField(max_length=1500)
    product = models.ForeignKey(CollaborationProduct, on_delete=models.CASCADE)


class CollaborationProductPaymentReceipt(models.Model):
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
    validated = models.BooleanField(default=False)
    customer = models.ForeignKey(WaitingUser, on_delete=models.CASCADE, null=True)