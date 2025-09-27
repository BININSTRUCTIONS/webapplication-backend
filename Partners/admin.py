from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([Party,
                     CollaborationProduct,
                     CollaborationProductHasParty,
                     WaitingUser,
                     WaitingUserHasProduct,
                     CollaborationProductMessage, ProductPlan, CollaborationProductPaymentReceipt])
