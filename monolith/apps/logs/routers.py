class LogRouter:
    """
    A router to control all database operations on models in the
    log application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read log models go to go_service.
        """
        if model._meta.app_label == "apps.logs":
            return "go_service"
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write log models go to go_service.
        """
        if model._meta.app_label == "apps.logs":
            return "go_service"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the log app.
        """
        if obj1._meta.app_label == "apps.logs" and obj2._meta.app_label == "apps.logs":
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the log app only appears in the 'go_service'
        database.
        """
        if app_label == "apps.logs":
            return db == "go_service"
        return None
