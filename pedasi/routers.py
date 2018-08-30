class DefaultRouter:
    """
    Django database router to route all models to the default database.
    """

    db_name = 'default'

    def db_for_read(self, model, **hints):
        """
        Read from default database.
        """
        return self.db_name

    def db_for_write(self, model, **hints):
        """
        Write to default database.
        """
        return self.db_name

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relation if both objects are stored in the default database.
        """
        if obj1._state.db == self.db_name and obj2._state.db == self.db_name:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Always allow migrations.
        """
        return True
