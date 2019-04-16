from django.urls import include, path

from rest_framework_nested import routers

from .views import (
    DataSourceApiViewset,
    QualityCriterionApiViewset,
    QualityLevelApiViewset,
    QualityRulesetApiViewset
)

app_name = 'api'

# Register ViewSets
router = routers.DefaultRouter()
router.register('datasources', DataSourceApiViewset)

# router = routers.SimpleRouter()

router.register('rulesets', QualityRulesetApiViewset, base_name='rulesets')
ruleset_router = routers.NestedSimpleRouter(router, 'rulesets', lookup='ruleset')
ruleset_router.register('levels', QualityLevelApiViewset, base_name='levels')

level_router = routers.NestedSimpleRouter(ruleset_router, 'levels', lookup='level')
level_router.register('criteria', QualityCriterionApiViewset, base_name='criteria')

urlpatterns = [
    path('',
         include(router.urls)),

    path('',
         include(ruleset_router.urls)),

    path('',
         include(level_router.urls)),
]
