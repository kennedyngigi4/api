

class AuthRouter:
    route_app_labels = { "auth", "contenttypes", "sessions", "admin", "accounts" }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "accounts"
        return None

    
    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "accounts"
        return None


    def allow_relation(self, obj1, obj2, **hints):
        if( obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None


    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "accounts"
        return None





class Listings:
    route_app_labels = { "listings" }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "listings"
        return None

    
    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "listings"
        return None


    def allow_relation(self, obj1, obj2, **hints):
        if( obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None


    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "listings"
        return None




class Payments:
    route_app_labels = { "payments" }


    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "payments"
        return None


    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "payments"
        return None


    def allow_relation(self, obj1, obj2, **hints):
        if( obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None


    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "payments"
        return None




class Marketing:
    route_app_labels = { "marketing" }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "marketing"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "marketing"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if( obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "marketing"
        return None
    


class Whatsappbot:
    route_app_labels = { "whatsappbot" }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "whatsappbot"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "whatsappbot"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if( obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "whatsappbot"
        return None



class Management:
    route_app_labels = { "management" }

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "management"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "management"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if( obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "management"
        return None





