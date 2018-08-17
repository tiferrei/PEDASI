from django.contrib import admin

from . import models


class DataSourceAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.DataSource, DataSourceAdmin)
