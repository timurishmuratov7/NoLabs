import asyncio
from typing import Annotated, Union, List

from fastapi import WebSocket, APIRouter, Depends, UploadFile, File, Form

from nolabs.api_models.conformations import RunSimulationsRequest, RunSimulationsResponse, ExperimentMetadataResponse, \
    GetExperimentResponse, ChangeExperimentNameRequest, GenerateUuidResponse, IntegratorsRequest
from nolabs.api_models.problem_details import ProblemDetailsResponse
from nolabs.controllers.conformations.dependencies import events_queue_dependency
from nolabs.controllers.conformations.dependencies import run_simulations_feature_dependency, \
    get_experiment_feature_dependency, delete_experiment_feature_dependency, \
    change_experiment_name_dependency, get_experiments_feature_dependency
from nolabs.features.conformations import DeleteExperimentFeature, RunSimulationsFeature, \
    GetExperimentsFeature, GetExperimentFeature, ChangeExperimentNameFeature
from nolabs.features.events_queue import EventsQueue, EventsQueueMessageClass
from nolabs.utils import uuid_utils

router = APIRouter(
    prefix='/api/v1/conformations',
    tags=['conformations']
)


@router.websocket("/logs")
async def ws(websocket: WebSocket, events_queue: Annotated[EventsQueue, Depends(events_queue_dependency)]):
    await websocket.accept()
    while True:
        data = events_queue.get_json(EventsQueueMessageClass.conformations)
        if data:
            await websocket.send_json(data)
        await asyncio.sleep(0.1)


@router.post('/inference')
async def inference(
        feature: Annotated[RunSimulationsFeature, Depends(run_simulations_feature_dependency)],
        pdb_file: UploadFile = File(),
        experiment_name: str = Form(),
        experiment_id: str = Form(None),
        total_frames: int = Form(10000),
        temperature_k: float = Form(273.15),
        take_frame_every: int = Form(1000),
        step_size: float = Form(0.002),
        replace_non_standard_residues: bool = Form(default=False),
        add_missing_atoms: bool = Form(default=False),
        add_missing_hydrogens: bool = Form(True),
        friction_coeff: float = Form(1.0),
        ignore_missing_atoms: bool = Form(default=False),
        integrator: IntegratorsRequest = Form(default=IntegratorsRequest.langevin),
) -> Union[RunSimulationsResponse, ProblemDetailsResponse]:
    global logs_websocket

    return await feature.handle(RunSimulationsRequest(
        pdb_file=pdb_file,
        experiment_name=experiment_name,
        experiment_id=experiment_id,
        total_frames=total_frames,
        temperature_k=temperature_k,
        take_frame_every=take_frame_every,
        step_size=step_size,
        replace_non_standard_residues=replace_non_standard_residues,
        add_missing_atoms=add_missing_atoms,
        add_missing_hydrogens=add_missing_hydrogens,
        friction_coeff=friction_coeff,
        ignore_missing_atoms=ignore_missing_atoms,
        integrator=integrator,
    ))


@router.get('/experiments')
async def experiments(feature: Annotated[GetExperimentsFeature, Depends(get_experiments_feature_dependency)]) -> List[
    ExperimentMetadataResponse]:
    return feature.handle()


@router.get('/get-experiment')
async def get_experiment(experiment_id: str, feature: Annotated[
    GetExperimentFeature, Depends(get_experiment_feature_dependency)]) -> GetExperimentResponse:
    return feature.handle(experiment_id)


@router.delete('/delete-experiment')
async def delete_experiment(experiment_id: str, feature: Annotated[
    DeleteExperimentFeature, Depends(delete_experiment_feature_dependency)]):
    return feature.handle(experiment_id)


@router.post('/change-experiment-name')
async def change_experiment_name(request: ChangeExperimentNameRequest, feature: Annotated[
    ChangeExperimentNameFeature, Depends(change_experiment_name_dependency)]):
    return feature.handle(request)


@router.get('/generate_id')
async def generate_uuid() -> GenerateUuidResponse:
    return GenerateUuidResponse(uuid=uuid_utils.generate_uuid())