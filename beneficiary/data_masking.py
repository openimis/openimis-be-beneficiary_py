from core.data_masking import DataMaskAbs
from beneficiary.apps import BeneficiaryConfig


class BeneficiaryMask(DataMaskAbs):
    masking_model = 'Beneficiary'
    anon_fields = BeneficiaryConfig.beneficiary_mask_fields
    masking_enabled = BeneficiaryConfig.social_protection_masking_enabled


class GroupBeneficiaryMask(DataMaskAbs):
    masking_model = 'GroupBeneficiary'
    anon_fields = BeneficiaryConfig.group_beneficiary_mask_fields
    masking_enabled = BeneficiaryConfig.social_protection_masking_enabled
