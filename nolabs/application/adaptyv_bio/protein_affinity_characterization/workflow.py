import uuid
from typing import List, Type

from bson import ObjectId
from pydantic import BaseModel

from nolabs.application.adaptyv_bio.api_proxy import AdaptyvBioProteinAffinityCharacterizationApi
from nolabs.domain.exceptions import NoLabsException, ErrorCodes
from nolabs.domain.models.adaptyv_bio.protein_affinity_characterization_job import ProteinAffinityCharacterizationJob
from nolabs.domain.models.common import JobId, JobName, Protein
from nolabs.infrastructure.settings import settings
from nolabs.workflow.core.component import Component, TOutput, TInput
from nolabs.workflow.core.flow import ComponentFlowHandler


class ProteinAffinityCharacterizationInput(BaseModel):
    protein_ids: List[uuid.UUID]


class ProteinAffinityCharacterizationOutput(BaseModel):
    pass


class ProteinAffinityCharacterizationFlowHandler(ComponentFlowHandler):
    async def on_start(self, inp: ProteinAffinityCharacterizationInput) -> List[uuid.UUID]:
        if not settings.adaptyv_bio_api_token:
            raise NoLabsException(ErrorCodes.adaptyv_bio_token_not_set)

        if not settings.adaptyv_bio_api_base:
            raise NoLabsException(ErrorCodes.adaptyv_bio_token_not_set)

        protein_ids = inp.protein_ids
        job: ProteinAffinityCharacterizationJob = ProteinAffinityCharacterizationJob.objects(
            proteins__in=protein_ids).first()
        if not job:
            # create a job
            job: ProteinAffinityCharacterizationJob = ProteinAffinityCharacterizationJob.create(
                id=JobId(uuid.uuid4()),
                name=JobName(f"{str(len(inp.protein_ids))} proteins"),
                component=self.component_id
            )
            proteins = Protein.objects(id__in=inp.protein_ids)
            job.set_proteins(proteins=proteins)
            await job.save()

        if len(job.proteins) == len(inp.protein_ids):
            return [job.id]

        raise NoLabsException(ErrorCodes.proteins_are_part_of_another_job, "Proteins some or all of the proteins are used in another job\experiment")

    async def on_job_start(self, job_id: uuid.UUID):
        job: ProteinAffinityCharacterizationJob = ProteinAffinityCharacterizationJob.objects.with_id(job_id)

        if not job:
            raise NoLabsException(ErrorCodes.job_not_found)

        job.input_errors(throw=True)

        sequences = [p.get_fasta() for p in job.proteins]

        api = AdaptyvBioProteinAffinityCharacterizationApi()
        api.submit_experiment(
            sequences=sequences,
            target_id=job.target_id,
            email=job.report_email,
            session_url=job.session_url,
            n_replicates=job.replicates,
            cart_total=job.cart_total,
            avg_length=job.dna_length,
            n_designs=job.number_of_designs
        )


class ProteinAffinityCharacterizationComponent(
    Component[ProteinAffinityCharacterizationInput, ProteinAffinityCharacterizationOutput]):
    name = 'Protein affinity characterization'
    description = 'Protein affinity characterization (Adaptyv bio)'

    @property
    def input_parameter_type(self) -> Type[TInput]:
        return ProteinAffinityCharacterizationInput

    @property
    def output_parameter_type(self) -> Type[TOutput]:
        return ProteinAffinityCharacterizationOutput

    @property
    def component_flow_type(self) -> Type["ComponentFlowHandler"]:
        return ProteinAffinityCharacterizationFlowHandler
