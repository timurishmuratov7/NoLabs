from typing import Annotated

from fastapi import Depends

from nolabs.controllers.common_dependencies import settings_dependency, dt_utils_dependency
from nolabs.features.drug_discovery import GetExperimentsFeature, DeleteExperimentFeature, \
    ChangeExperimentNameFeature
from nolabs.features.drug_discovery import RunGeneOntologyFeature
from nolabs.features.drug_discovery.services.file_management import FileManagement
from nolabs.infrastructure.settings import Settings
from nolabs.utils import DateTimeUtils


def file_management_dependency(settings: Annotated[Settings, Depends(settings_dependency)],
                               dt_utils: Annotated[DateTimeUtils, Depends(dt_utils_dependency)]) -> FileManagement:
    return FileManagement(settings=settings, dt_utils=dt_utils)


def run_gene_ontology_feature_dependency() -> RunGeneOntologyFeature:
    return RunGeneOntologyFeature()


def get_experiments_feature_dependency(
        file_management: Annotated[FileManagement, Depends(file_management_dependency)]) -> GetExperimentsFeature:
    return GetExperimentsFeature(file_management=file_management)


def get_experiment_feature_dependency(
        file_management: Annotated[FileManagement, Depends(file_management_dependency)]) -> GetExperimentFeature:
    return GetExperimentFeature(file_management=file_management)


def delete_experiment_feature_dependency(
        file_management: Annotated[FileManagement, Depends(file_management_dependency)]) -> DeleteExperimentFeature:
    return DeleteExperimentFeature(file_management=file_management)


def change_experiment_name_dependency(
        file_management: Annotated[FileManagement, Depends(file_management_dependency)]
) -> ChangeExperimentNameFeature:
    return ChangeExperimentNameFeature(
        file_management=file_management
    )
