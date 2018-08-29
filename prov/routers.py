class ProvRouter:
    db_name = 'prov'
    app_label = 'prov'

    def db_for_read(self, model, **hints):
        """
        Read from default database.
        """
        if model._meta.app_label == self.app_label:
            return self.db_name
        return None

    def db_for_write(self, model, **hints):
        """
        Write to default database.
        """
        if model._meta.app_label == self.app_label:
            return self.db_name
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relation if a model in this app is involved.
        """
        if obj1._meta.app_label == self.app_label or obj2._meta.app_label == self.app_label:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Always allow migrations.
        """
        if app_label == self.app_label:
            return db == self.db_name
