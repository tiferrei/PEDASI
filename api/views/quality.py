"""
This module contains the API for data quality rulesets.
"""

from django.shortcuts import get_object_or_404

from rest_framework import viewsets


from datasources import models, serializers
from .. import permissions


class QualityRulesetApiViewset(viewsets.ModelViewSet):
    serializer_class = serializers.QualityRulesetSerializer
    permission_classes = [permissions.IsAdminOrReadOnly]

    def get_queryset(self):
        return models.QualityRuleset.objects.all()


class QualityLevelApiViewset(viewsets.ModelViewSet):
    serializer_class = serializers.QualityLevelSerializer
    permission_classes = [permissions.IsAdminOrReadOnly]

    def get_queryset(self):
        return models.QualityLevel.objects.filter(ruleset=self.kwargs['ruleset_pk'])

    def get_object(self):
        return self.get_queryset().get(level=self.kwargs['pk'])

    def perform_create(self, serializer):
        ruleset = get_object_or_404(models.QualityRuleset, pk=self.kwargs['ruleset_pk'])
        serializer.save(ruleset=ruleset)


class QualityCriterionApiViewset(viewsets.ModelViewSet):
    queryset = models.QualityCriterion.objects.all()
    serializer_class = serializers.QualityCriterionSerializer
    permission_classes = [permissions.IsAdminOrReadOnly]

    def get_queryset(self):
        return models.QualityCriterion.objects.filter(
            quality_level__ruleset=self.kwargs['ruleset_pk'],
            quality_level__level=self.kwargs['level_pk']
        )

    def perform_create(self, serializer):
        level = get_object_or_404(models.QualityLevel,
                                  ruleset=self.kwargs['ruleset_pk'],
                                  level=self.kwargs['level_pk'])
        serializer.save(quality_level=level)
