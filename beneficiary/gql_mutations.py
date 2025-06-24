import graphene as graphene
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db import transaction

from core.gql.gql_mutations.base_mutation import (
    BaseHistoryModelCreateMutationMixin,
    BaseMutation,
    BaseHistoryModelUpdateMutationMixin,
    BaseHistoryModelDeleteMutationMixin
)
from core.schema import OpenIMISMutation
from beneficiary.apps import BeneficiaryConfig
from beneficiary.models import (
    Beneficiary, GroupBeneficiary, BeneficiaryStatus
)
from beneficiary.services import (
    BeneficiaryService,
    GroupBeneficiaryService
)


def check_perms_for_field(user, permission, data, field_string):
    if data.get(field_string, None) and not user.has_perms(permission):
        raise ValidationError("mutation.lack_of_schema_perms")


class CreateGenericBeneficiaryInputType(OpenIMISMutation.Input):
    class BeneficiaryStatusEnum(graphene.Enum):
        POTENTIAL = BeneficiaryStatus.POTENTIAL
        ACTIVE = BeneficiaryStatus.ACTIVE
        GRADUATED = BeneficiaryStatus.GRADUATED
        SUSPENDED = BeneficiaryStatus.SUSPENDED

    status = graphene.Field(BeneficiaryStatusEnum, required=True)
    benefit_plan_id = graphene.UUID(required=False)

    date_valid_from = graphene.Date(required=False)
    date_valid_to = graphene.Date(required=False)
    json_ext = graphene.types.json.JSONString(required=False)

    def resolve_status(self, info):
        return self.status


class UpdateGenericBeneficiaryInputType(CreateGenericBeneficiaryInputType):
    id = graphene.UUID(required=True)


class CreateBeneficiaryInputType(CreateGenericBeneficiaryInputType):
    individual_id = graphene.UUID(required=False)


class CreateGroupBeneficiaryInputType(CreateGenericBeneficiaryInputType):
    group_id = graphene.UUID(required=False)


class UpdateBeneficiaryInputType(UpdateGenericBeneficiaryInputType):
    pass


class UpdateGroupBeneficiaryInputType(UpdateGenericBeneficiaryInputType):
    pass


class CreateBeneficiaryMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_class = "CreateBeneficiaryMutation"
    _mutation_module = "beneficiary"
    _model = Beneficiary

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.has_perms(
                BeneficiaryConfig.gql_beneficiary_create_perms):
            raise ValidationError("mutation.authentication_required")
        check_perms_for_field(
            user, BeneficiaryConfig.gql_schema_create_perms, data, 'json_ext'
        )

    @classmethod
    def _mutate(cls, user, **data):
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')

        service = BeneficiaryService(user)
        if BeneficiaryConfig.gql_check_beneficiary_crud:
            res = service.create_create_task(data)
        else:
            res = service.create(data)

        return res if not res['success'] else None

    class Input(CreateBeneficiaryInputType):
        pass


class UpdateBeneficiaryMutation(BaseHistoryModelUpdateMutationMixin, BaseMutation):
    _mutation_class = "UpdateBeneficiaryMutation"
    _mutation_module = "beneficiary"
    _model = Beneficiary

    @classmethod
    def _validate_mutation(cls, user, **data):
        super()._validate_mutation(user, **data)
        if type(user) is AnonymousUser or not user.has_perms(
                BeneficiaryConfig.gql_beneficiary_update_perms):
            raise ValidationError("mutation.authentication_required")
        check_perms_for_field(
            user, BeneficiaryConfig.gql_schema_update_perms, data, 'json_ext'
        )

    @classmethod
    def _mutate(cls, user, **data):
        if "date_valid_to" not in data:
            data['date_valid_to'] = None
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')

        service = BeneficiaryService(user)
        if BeneficiaryConfig.gql_check_beneficiary_crud:
            res = service.create_update_task(data)
        else:
            res = service.update(data)

        return res if not res['success'] else None

    class Input(UpdateBeneficiaryInputType):
        pass


class DeleteBeneficiaryMutation(BaseHistoryModelDeleteMutationMixin, BaseMutation):
    _mutation_class = "DeleteBeneficiaryMutation"
    _mutation_module = "beneficiary"
    _model = Beneficiary

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                BeneficiaryConfig.gql_beneficiary_delete_perms):
            raise ValidationError("mutation.authentication_required")

    @classmethod
    def _mutate(cls, user, **data):
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')

        service = BeneficiaryService(user)

        ids = data.get('ids')
        if not ids:
            return {'success': False, 'message': 'No IDs to delete', 'details': ''}

        with transaction.atomic():
            for obj_id in ids:
                if BeneficiaryConfig.gql_check_beneficiary_crud:
                    res = service.create_delete_task({'id': obj_id})
                else:
                    res = service.delete({'id': obj_id, 'user': user})
                if not res['success']:
                    transaction.rollback()
                    return res

    class Input(OpenIMISMutation.Input):
        ids = graphene.List(graphene.UUID)


class CreateGroupBeneficiaryMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_class = "CreateGroupBeneficiaryMutation"
    _mutation_module = "beneficiary"
    _model = GroupBeneficiary

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.has_perms(
                BeneficiaryConfig.gql_beneficiary_create_perms):
            raise ValidationError("mutation.authentication_required")
        check_perms_for_field(
            user, BeneficiaryConfig.gql_schema_create_perms, data, 'json_ext'
        )

    @classmethod
    def _mutate(cls, user, **data):
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')

        service = GroupBeneficiaryService(user)
        if BeneficiaryConfig.gql_check_group_beneficiary_crud:
            res = service.create_create_task(data)
        else:
            res = service.create(data)

        return res if not res['success'] else None

    class Input(CreateGroupBeneficiaryInputType):
        pass


class UpdateGroupBeneficiaryMutation(BaseHistoryModelUpdateMutationMixin, BaseMutation):
    _mutation_class = "UpdateGroupBeneficiaryMutation"
    _mutation_module = "beneficiary"
    _model = GroupBeneficiary

    @classmethod
    def _validate_mutation(cls, user, **data):
        super()._validate_mutation(user, **data)
        if type(user) is AnonymousUser or not user.has_perms(
                BeneficiaryConfig.gql_beneficiary_update_perms):
            raise ValidationError("mutation.authentication_required")
        check_perms_for_field(
            user, BeneficiaryConfig.gql_schema_update_perms, data, 'json_ext'
        )

    @classmethod
    def _mutate(cls, user, **data):
        if "date_valid_to" not in data:
            data['date_valid_to'] = None
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')

        service = GroupBeneficiaryService(user)
        if BeneficiaryConfig.gql_check_group_beneficiary_crud:
            res = service.create_update_task(data)
        else:
            res = service.update(data)

        return res if not res['success'] else None

    class Input(UpdateGroupBeneficiaryInputType):
        pass


class DeleteGroupBeneficiaryMutation(BaseHistoryModelDeleteMutationMixin, BaseMutation):
    _mutation_class = "DeleteGroupBeneficiaryMutation"
    _mutation_module = "beneficiary"
    _model = GroupBeneficiary

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                BeneficiaryConfig.gql_beneficiary_delete_perms):
            raise ValidationError("mutation.authentication_required")

    @classmethod
    def _mutate(cls, user, **data):
        if "client_mutation_id" in data:
            data.pop('client_mutation_id')
        if "client_mutation_label" in data:
            data.pop('client_mutation_label')

        service = GroupBeneficiaryService(user)

        ids = data.get('ids')
        if not ids:
            return {'success': False, 'message': 'No IDs to delete', 'details': ''}

        with transaction.atomic():
            for obj_id in ids:
                if BeneficiaryConfig.gql_check_group_beneficiary_crud:
                    res = service.create_delete_task({'id': obj_id})
                else:
                    res = service.delete({'id': obj_id, 'user': user})
                if not res['success']:
                    transaction.rollback()
                    return res

    class Input(OpenIMISMutation.Input):
        ids = graphene.List(graphene.UUID)
