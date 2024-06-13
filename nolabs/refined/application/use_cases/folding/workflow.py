import uuid
from typing import List, Type

from pydantic import BaseModel

from nolabs.refined.application.use_cases.folding.api_models import FoldingBackendEnum, SetupJobRequest
from nolabs.refined.application.use_cases.folding.use_cases import SetupJobFeature, RunJobFeature, GetJobFeature
from nolabs.refined.domain.models.common import Protein
from nolabs.refined.domain.models.folding import FoldingJob
from nolabs.refined.infrastructure.di import InfrastructureDependencies
from nolabs.workflow.component import Component, JobValidationError


class FoldingComponentInput(BaseModel):
    proteins_with_fasta: List[uuid.UUID]
    backend: FoldingBackendEnum = FoldingBackendEnum.esmfold_light


class FoldingComponentOutput(BaseModel):
    proteins_with_pdb: List[uuid.UUID]


class FoldingComponent(Component[FoldingComponentInput, FoldingComponentOutput]):
    name = 'Folding'

    async def execute(self):
        print('ONE')
        run_job_feature = RunJobFeature(
            esmfold=InfrastructureDependencies.esmfold_microservice(),
            esmfold_light=InfrastructureDependencies.esmfold_light_microservice(),
            rosettafold=InfrastructureDependencies.rosettafold_microservice()
        )
        get_job_feature = GetJobFeature()

        for job in self.jobs:
            await run_job_feature.handle(job_id=job.id)

        items: List[uuid.UUID] = []

        for job in self.jobs:
            get_result = await get_job_feature.handle(job_id=job.id)

            for protein_id in get_result.protein_ids:
                items.append(protein_id)

        self.output = FoldingComponentOutput(
            proteins_with_pdb=items
        )

    async def setup_jobs(self):
        setup_job_feature = SetupJobFeature()

        self.jobs = []

        for protein_id in self.input.proteins_with_fasta:
            protein = Protein.objects.with_id(protein_id)

            result = await setup_job_feature.handle(request=SetupJobRequest(
                experiment_id=self.experiment.id,
                backend=self.input.backend,
                protein_ids=[protein.id],
                job_name=f'Folding {protein.name.fasta_name}'
            ))

            self.jobs.append(FoldingJob.objects.with_id(result.job_id))

    async def prevalidate_jobs(self) -> List[JobValidationError]:
        validation_errors = []

        job: FoldingJob
        for job in self.jobs:
            if not job.proteins:
                validation_errors.append(
                    JobValidationError(
                        job_id=job.id,
                        msg=f'No proteins'
                    )
                )

        return validation_errors

    @property
    def _input_parameter_type(self) -> Type[FoldingComponentInput]:
        return FoldingComponentInput

    @property
    def _output_parameter_type(self) -> Type[FoldingComponentOutput]:
        return FoldingComponentOutput

    async def executing(self) -> bool:
        job: FoldingJob

        esmfold_api = InfrastructureDependencies.esmfold_microservice()
        esmfold_light_api = InfrastructureDependencies.esmfold_light_microservice()
        rosettafold_api = InfrastructureDependencies.rosettafold_microservice()

        for job in self.jobs:
            if job.backend == FoldingBackendEnum.esmfold_light:
                status = esmfold_light_api.is_job_running_job_job_id_is_running_get(
                    job_id=job.id
                )
                if status.is_running:
                    return True

            if job.backend == FoldingBackendEnum.esmfold_light:
                status = esmfold_api.is_job_running_job_job_id_is_running_get(
                    job_id=job.id
                )
                if not not status:
                    return True

            if job.backend == FoldingBackendEnum.esmfold_light:
                status = rosettafold_api.is_job_running_job_job_id_is_running_get(
                    job_id=job.id
                )
                if status.is_running:
                    return True

        return False