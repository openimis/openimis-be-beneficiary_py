from django.utils.translation import gettext as _

from core.validation import BaseModelValidation
from beneficiary.models import Beneficiary


def validate_not_empty_field(string, field):
    if not string:
        return [{"message": _("beneficiary.validation.field_empty") % {
            'field': field
        }}]
    return []


class BeneficiaryValidation(BaseModelValidation):
    OBJECT_TYPE = Beneficiary


class GroupBeneficiaryValidation(BaseModelValidation):
    OBJECT_TYPE = Beneficiary
