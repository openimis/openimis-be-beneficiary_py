from django.apps import AppConfig

from core.data_masking import MaskingClassRegistryPoint


DEFAULT_CONFIG = {
    "gql_beneficiary_search_perms": ["170001"],
    "gql_beneficiary_create_perms": ["170002"],
    "gql_beneficiary_update_perms": ["170003"],
    "gql_beneficiary_delete_perms": ["170004"],

    # Create task for model instead of performing crud action
    "gql_check_beneficiary_crud": True,
    "gql_check_group_beneficiary_crud": True,
    "enable_maker_checker_for_beneficiary_upload": True,
    "enable_maker_checker_for_beneficiary_update": True,
    "validation_import_valid_items": "validation.import_valid_items",
    "validation_import_valid_items": "validation.import_valid_items",
    "validation_import_group_valid_items": "validation.import_group_valid_items",
    "validation_upload_valid_items": "validation.upload_valid_items",
    "validation_download_invalid_items": "validation.download_invalid_items",

    "validation_import_valid_items_workflow": "beneficiary-import-valid-items.beneficiary-import-valid-items",
    "validation_upload_valid_items_workflow": "beneficiary-upload-valid-items.beneficiary-upload-valid-items",
    "validation_enrollment": "validation-enrollment",
    "validation_group_enrollment": "validation-group-enrollment",

    "enable_maker_checker_logic_enrollment": True,
    "enable_maker_checker_for_group_upload": True,
    "beneficiary_mask_fields": [
        'json_ext.beneficiary_data_source',
        'json_ext.educated_level'
    ],
    "group_beneficiary_mask_fields": [
        'json_ext.beneficiary_data_source',
        'json_ext.educated_level'
    ],
    "beneficiary_base_fields": [
        'first_name', 'last_name', 'dob', 'location_name', 'location_code', 'id'
    ],
    "beneficiary_masking_enabled": True,
    "enable_python_workflows": True,
    "default_beneficiary_status": "POTENTIAL",
}


class BeneficiaryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'beneficiary'
    verbose_name = 'Beneficiary'

    gql_beneficiary_search_perms = None
    gql_beneficiary_create_perms = None
    gql_beneficiary_update_perms = None
    gql_beneficiary_delete_perms = None

    gql_check_beneficiary_crud = None
    gql_check_group_beneficiary_crud = None
    validation_import_valid_items = None
    validation_upload_valid_items = None
    validation_download_invalid_items = None
    validation_import_valid_items_workflow = None
    validation_upload_valid_items_workflow = None
    validation_enrollment = None
    validation_group_enrollment = None
    validation_import_group_valid_items = None

    enable_maker_checker_for_beneficiary_upload = None
    enable_maker_checker_for_beneficiary_update = None

    enable_python_workflows = None
    enable_maker_checker_logic_enrollment = None
    enable_maker_checker_for_group_upload = None
    beneficiary_mask_fields = None
    group_beneficiary_mask_fields = None
    beneficiary_base_fields = None
    beneficiary_masking_enabled = None

    default_beneficiary_status = None

    def ready(self):
        from core.models import ModuleConfiguration

        cfg = ModuleConfiguration.get_or_default(self.name, DEFAULT_CONFIG)
        self.__load_config(cfg)
        self._set_up_workflows()
        self.__register_masking_class()

    def _set_up_workflows(self):
        from workflow.systems.python import PythonWorkflowAdaptor
        from beneficiary.workflows import process_import_beneficiaries_workflow, \
            process_update_beneficiaries_workflow, \
            process_import_valid_beneficiaries_workflow, \
            process_update_valid_beneficiaries_workflow

        if self.enable_python_workflows:
            PythonWorkflowAdaptor.register_workflow(
                'Python Beneficiaries Upload',
                'beneficiary',
                process_import_beneficiaries_workflow
            )
            PythonWorkflowAdaptor.register_workflow(
                'Python Beneficiaries Update',
                'beneficiary',
                process_update_beneficiaries_workflow
            )
            PythonWorkflowAdaptor.register_workflow(
                'Python Beneficiaries Valid Upload',
                'beneficiary',
                process_import_valid_beneficiaries_workflow
            )
            PythonWorkflowAdaptor.register_workflow(
                'Python Beneficiaries Valid Update',
                'beneficiary',
                process_update_valid_beneficiaries_workflow
            )

        # Replace default setup for invalid workflow to be python one
        if BeneficiaryConfig.enable_python_workflows is True:

            # Resolve Maker-Checker Workflows Overwrite
            if self.validation_import_valid_items_workflow == DEFAULT_CONFIG['validation_import_valid_items_workflow']:
                BeneficiaryConfig.validation_import_valid_items_workflow \
                    = 'beneficiary.Python Beneficiaries Valid Upload'

            if self.validation_upload_valid_items_workflow == DEFAULT_CONFIG['validation_upload_valid_items_workflow']:
                BeneficiaryConfig.validation_upload_valid_items_workflow \
                    = 'beneficiary.Python Beneficiaries Valid Update'

    @classmethod
    def __load_config(cls, cfg):
        """
        Load all config fields that match current AppConfig class fields, all custom fields have to be loaded separately
        """
        for field in cfg:
            if hasattr(BeneficiaryConfig, field):
                setattr(BeneficiaryConfig, field, cfg[field])

    def __register_masking_class(cls):
        from beneficiary.data_masking import (
            BeneficiaryMask,
            GroupBeneficiaryMask
        )
        MaskingClassRegistryPoint.register_masking_class(
            masking_class_list=[BeneficiaryMask(), GroupBeneficiaryMask()]
        )

    @staticmethod
    def get_beneficiary_upload_file_path(benefit_plan_id, file_name=None):
        if file_name:
            return f"beneficiary_upload/benefit_plan_{benefit_plan_id}/{file_name}"
        return f"beneficiary_upload/benefit_plan_{benefit_plan_id}"
