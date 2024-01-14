from nolabs.api_models.drug_discovery import UploadTargetRequest, UploadTargetResponse, \
    GetTargetsListRequest, GetTargetsListResponse, DeleteTargetRequest, DeleteTargetResponse
from nolabs.domain.experiment import ExperimentId
from nolabs.features.drug_discovery.data_models.target import TargetId
from nolabs.features.drug_discovery.services.target_file_management import TargetsFileManagement

class UploadTargetFeature:
    def __init__(self, file_management: TargetsFileManagement):
        self._file_management = file_management

    def handle(self, request: UploadTargetRequest) -> UploadTargetResponse:
        assert request

        experiment_id = ExperimentId(request.experiment_id)
        protein_file = request.fasta_file

        response = self._file_management.store_target(experiment_id, protein_file)

        return UploadTargetResponse(result=response)

class DeleteTargetFeature:
    def __init__(self, file_management: TargetsFileManagement):
        self._file_management = file_management

    def handle(self, request: DeleteTargetRequest) -> DeleteTargetResponse:
        assert request

        experiment_id = ExperimentId(request.experiment_id)
        target_id = TargetId(request.target_id)

        deleted_target_id = self._file_management.delete_target(experiment_id, target_id)

        return DeleteTargetResponse(target_id=deleted_target_id)

class GetTargetsListFeature:
    def __init__(self, file_management: TargetsFileManagement):
        self._file_management = file_management

    def handle(self, request: GetTargetsListRequest) -> GetTargetsListResponse:
        assert request

        experiment_id = ExperimentId(request.experiment_id)

        targets = self._file_management.get_targets_list(experiment_id)

        return GetTargetsListResponse(targets=targets)