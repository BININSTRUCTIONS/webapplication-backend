from django.contrib import admin
from .models import *


# Register your models here.

admin.site.register(
    [
        ApplicationType,
        ProjectStatus,
        Order,
        Customer,
        Employee,
        ProjectDiscussion,
        ProjectDiscussionHasStaff,
        Message,
        Admin,
        Product,
        Designation,
        ProductMedia,
        ProductOrder,
        PaymentStatus,
        ProjectHasEmployees,
        LicenseKey,
        AccountType,
        PricePlan,
        CustomersHavePlans,
        PaymentReceipt
    ]
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "order_id", "user", "project_status", "project_type"]
    # fields = ["name", "proposal", "proposal_link", "design_files", "design_link", "srs", "type", "order", "status", "start_date", "end_date"]

    def order_id(self, obj: Project) -> str:
        return str(obj.order.id)

    def user(self, obj: Project) -> str:
        return str(obj.order.user.username)

    def project_status(self, obj: Project) -> str:
        return str(obj.status.status)

    def project_type(self, obj: Project) -> str:
        return str(obj.type.type)
