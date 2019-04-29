from django.contrib import admin

from . import forms, models


@admin.register(models.MetadataField)
class MetadataFieldAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MetadataItem)
class MetadataItemAdmin(admin.ModelAdmin):
    pass


class MetadataItemInline(admin.TabularInline):
    model = models.MetadataItem
    readonly_fields = ('field', 'value',)
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    readonly_fields = ['owner']
    form = forms.DataSourceForm
    inlines = [
        MetadataItemInline,
    ]

    def has_change_permission(self, request, obj=None) -> bool:
        """
        Does the user have permission to change this object?
        """
        permission = super().has_change_permission(request, obj)

        if obj is not None:
            permission &= (obj.owner == request.user) or request.user.is_superuser

        return permission

    def has_delete_permission(self, request, obj=None) -> bool:
        """
        Does the user have permission to delete this object?
        """
        permission = super().has_delete_permission(request, obj)

        if obj is not None:
            permission &= (obj.owner == request.user) or request.user.is_superuser

        return permission

    def save_model(self, request, obj, form, change):
        """
        Set missing fields when model is saved.
        """
        try:
            owner = form.instance.owner

        except models.DataSource.owner.RelatedObjectDoesNotExist:
            form.instance.owner = request.user

        super().save_model(request, obj, form, change)


class PipelineStageInline(admin.TabularInline):
    model = models.PipelineStage
    readonly_fields = ('plugin_name',)
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    inlines = [
        PipelineStageInline,
    ]


@admin.register(models.PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    pass


@admin.register(models.QualityRuleset)
class QualityRulesetAdmin(admin.ModelAdmin):
    pass


@admin.register(models.QualityLevel)
class QualityLevelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.QualityCriterion)
class QualityCriterionAdmin(admin.ModelAdmin):
    pass
