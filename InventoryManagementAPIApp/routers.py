class CustomDBRouter:
    route_app_labels = {"inventorymanagementapiapp"}
    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "inventory_management_db"
        return None
    
    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "inventory_management_db"
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        db_set = {"default", "inventory_management_db"}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "inventorymanagementapiapp" and db == "inventory_management_db":
            return True
        return None