import graphene
from django.contrib.auth.models import AnonymousUser
from graphene_django import DjangoObjectType
import django_filters

from core import prefix_filterset, ExtendedConnection
from individual.gql_queries import IndividualGQLType, GroupGQLType, \
    IndividualDataSourceUploadGQLType
from beneficiary.apps import BeneficiaryConfig
from beneficiary.models import (
    Beneficiary, GroupBeneficiary, BenefitPlanDataUploadRecords
)
from social_protection.models import BenefitPlan
from social_protection.gql_queries import BenefitPlanGQLType


def _have_permissions(user, permission):
    if isinstance(user, AnonymousUser):
        return False
    if not user.id:
        return False
    return user.has_perms(permission)


class JsonExtMixin:
    def resolve_json_ext(self, info):
        if _have_permissions(info.context.user, BeneficiaryConfig.gql_schema_search_perms):
            return self.json_ext
        return None

class BeneficiaryFilter(django_filters.FilterSet):
    is_eligible = django_filters.BooleanFilter(method='filter_is_eligible')

    class Meta:
        model = Beneficiary
        fields = {
            "id": ["exact"],
            "status": ["exact", "iexact", "startswith", "istartswith", "contains", "icontains"],
            "date_valid_from": ["exact", "lt", "lte", "gt", "gte"],
            "date_valid_to": ["exact", "lt", "lte", "gt", "gte"],
            **prefix_filterset("individual__", IndividualGQLType._meta.filter_fields),
            **prefix_filterset("benefit_plan__", BenefitPlanGQLType._meta.filter_fields),
            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "is_deleted": ["exact"],
            "version": ["exact"],
        }

    def filter_is_eligible(self, queryset, name, value):
        return queryset.filter(is_eligible=value)


class BeneficiaryGQLType(DjangoObjectType, JsonExtMixin):
    uuid = graphene.String(source='uuid')
    is_eligible = graphene.Boolean()

    class Meta:
        model = Beneficiary
        interfaces = (graphene.relay.Node,)
        filterset_class = BeneficiaryFilter
        connection_class = ExtendedConnection

    def resolve_is_eligible(self, info):
        return self.is_eligible


class GroupBeneficiaryFilter(django_filters.FilterSet):
    is_eligible = django_filters.BooleanFilter(method='filter_is_eligible')

    class Meta:
        model = GroupBeneficiary
        fields = {
            "id": ["exact"],
            "status": ["exact", "iexact", "startswith", "istartswith", "contains", "icontains"],
            "date_valid_from": ["exact", "lt", "lte", "gt", "gte"],
            "date_valid_to": ["exact", "lt", "lte", "gt", "gte"],
            **prefix_filterset("group__", GroupGQLType._meta.filter_fields),
            **prefix_filterset("benefit_plan__", BenefitPlanGQLType._meta.filter_fields),
            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "is_deleted": ["exact"],
            "version": ["exact"],
        }

    def filter_is_eligible(self, queryset, name, value):
        return queryset.filter(is_eligible=value)


class GroupBeneficiaryGQLType(DjangoObjectType, JsonExtMixin):
    uuid = graphene.String(source='uuid')
    is_eligible = graphene.Boolean()

    class Meta:
        model = GroupBeneficiary
        interfaces = (graphene.relay.Node,)
        filterset_class = GroupBeneficiaryFilter
        connection_class = ExtendedConnection

    def resolve_is_eligible(self, info):
        return self.is_eligible


class BenefitPlanDataUploadQGLType(DjangoObjectType, JsonExtMixin):
    uuid = graphene.String(source='uuid')

    class Meta:
        model = BenefitPlanDataUploadRecords
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "date_created": ["exact", "lt", "lte", "gt", "gte"],
            "date_updated": ["exact", "lt", "lte", "gt", "gte"],
            "is_deleted": ["exact"],
            "version": ["exact"],
            "workflow": ["exact", "iexact", "startswith", "istartswith", "contains", "icontains"],
            **prefix_filterset("data_upload__", IndividualDataSourceUploadGQLType._meta.filter_fields),
            **prefix_filterset("benefit_plan__", BenefitPlanGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection
