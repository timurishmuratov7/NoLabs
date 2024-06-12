import {
  ExperimentsService,
  FoldingService,
  type GetJobMetadataResponse,
  JobsACommonControllerForJobsManagementService,
  type nolabs__refined__application__use_cases__folding__api_models__GetJobStatusResponse,
  type nolabs__refined__application__use_cases__folding__api_models__JobResponse,
  type ProteinResponse,
  ProteinsService,
  nolabs__refined__application__use_cases__folding__api_models__SetupJobRequest,
  UpdateJobRequest,
  WorkflowService,
  BiobuddyService,
  WorkflowSchemaModel_Output,
  AllWorkflowSchemasResponse,
  WorkflowSchemaModel_Input,
  ProteinSearchQuery,
  Body_upload_protein_api_v1_objects_proteins_post,
  Body_update_protein_api_v1_objects_proteins_patch,
  CheckBioBuddyEnabledResponse,
  LigandResponse,
  LigandSearchQuery,
  LigandsService,
  Body_upload_ligand_api_v1_objects_ligands_post,
  Body_update_ligand_api_v1_objects_ligands_patch,
  BindingPocketsService,
  nolabs__refined__application__use_cases__binding_pockets__api_models__JobResponse,
  nolabs__refined__application__use_cases__binding_pockets__api_models__GetJobStatusResponse
} from 'src/refinedApi/client';
import {CancelablePromise, ExperimentMetadataResponse} from "../../refinedApi/client";


export function getExperimentsApi(): CancelablePromise<Array<ExperimentMetadataResponse>> {
  return ExperimentsService.experimentsApiV1ExperimentsExperimentsAllGet();
}

export function createExperimentApi(): CancelablePromise<ExperimentMetadataResponse> {
  return ExperimentsService.createExperimentApiV1ExperimentsExperimentsPost();
}

export function getProtein(proteinId: string): CancelablePromise<(ProteinResponse | null)> {
  return ProteinsService.getProteinApiV1ObjectsProteinsProteinIdGet(proteinId);
}

// Delete an experiment
export function deleteExperimentApi(experimentId: string): CancelablePromise<any> {
  return ExperimentsService.deleteExperimentApiV1ExperimentsExperimentsExperimentIdDelete(experimentId);
}

export function getFoldingJobsApi(experimentId: string): CancelablePromise<Array<GetJobMetadataResponse>> {
  return JobsACommonControllerForJobsManagementService.jobsMetadataApiV1JobsJobsMetadataGet(experimentId);
}

export function getFoldingJobApi(jobId: string): CancelablePromise<nolabs__refined__application__use_cases__folding__api_models__JobResponse> {
  return FoldingService.getJobApiV1FoldingJobsJobIdGet(jobId);
}

export function getBindingPocketJobApi(jobId: string): CancelablePromise<nolabs__refined__application__use_cases__binding_pockets__api_models__JobResponse> {
  return BindingPocketsService.getJobApiV1BindingPocketsJobsJobIdGet(jobId);
}

export function getFoldingJobStatus(jobId: string): CancelablePromise<nolabs__refined__application__use_cases__folding__api_models__GetJobStatusResponse> {
  return FoldingService.getJobStatusApiV1FoldingJobsJobIdStatusGet(jobId);
}

export function getBindingPocketJobStatus(jobId: string): CancelablePromise<nolabs__refined__application__use_cases__binding_pockets__api_models__GetJobStatusResponse> {
  return BindingPocketsService.getJobStatusApiV1BindingPocketsJobsJobIdStatusGet(jobId);
}

export function setupFoldingJob(job: nolabs__refined__application__use_cases__folding__api_models__SetupJobRequest): CancelablePromise<nolabs__refined__application__use_cases__folding__api_models__JobResponse> {
  return FoldingService.setupJobApiV1FoldingJobsPost(job);
}

export function changeJobName(jobId: string, newName: string): CancelablePromise<any> {
  const jobRequest = { job_name: newName } as UpdateJobRequest;
  return JobsACommonControllerForJobsManagementService.updateApiV1JobsJobsJobIdPatch(jobId, jobRequest);
}

export function createWorkflow(experimentId: string): CancelablePromise<any> {
  return WorkflowService.createSchemaApiV1WorkflowExperimentIdPost(experimentId);
}

export function getWorkflow(workflowId: string): CancelablePromise<(WorkflowSchemaModel_Output | null)> {
  return WorkflowService.getSchemaApiV1WorkflowWorkflowIdGet(workflowId);
}

export function getExistingWorkflows(experimentId: string): CancelablePromise<AllWorkflowSchemasResponse> {
  return WorkflowService.getSchemaApiV1WorkflowAllExperimentIdGet(experimentId);
}

export function sendWorkflowUpdate(workflow: WorkflowSchemaModel_Input): CancelablePromise<any> {
  return WorkflowService.setWorkflowSchemaApiV1WorkflowPut(workflow)
}

export function startWorkflowforExperiment(experimentId: string): CancelablePromise<any> {
  return WorkflowService.startWorkflowApiV1WorkflowExperimentIdStartPost(experimentId)
}

export function getAllProteins(experimentId: string): CancelablePromise<Array<ProteinResponse>> {
  const searchQuery = {name: '', experiment_id: experimentId} as ProteinSearchQuery;
  return ProteinsService.searchProteinsApiV1ObjectsProteinsSearchPost(searchQuery);
}

export function uploadProtein(
  experimentId: string,
  name?: string,
  fasta?: Blob,
  pdb?: Blob
): CancelablePromise<ProteinResponse> {
  const uploadProtein = {
    experiment_id: experimentId,
    name: name,
    fasta: fasta,
    pdb: pdb
  } as Body_upload_protein_api_v1_objects_proteins_post;
  return ProteinsService.uploadProteinApiV1ObjectsProteinsPost(uploadProtein);
}

export function deleteProtein(proteinId: string): CancelablePromise<any> {
  return ProteinsService.deleteProteinApiV1ObjectsProteinsProteinIdDelete(proteinId);
}

export function updateProteinName(proteinId: string, newName: string): CancelablePromise<ProteinResponse> {
  const newRequest = {
    protein_id: proteinId,
    name: newName
  } as Body_update_protein_api_v1_objects_proteins_patch;
  return ProteinsService.updateProteinApiV1ObjectsProteinsPatch(newRequest);
}

export function getAllLigands(experimentId: string): CancelablePromise<Array<LigandResponse>> {
  const searchQuery = {name: '', experiment_id: experimentId} as LigandSearchQuery;
  return LigandsService.searchLigandsApiV1ObjectsLigandsSearchPost(searchQuery);
}

export function uploadLigand(
  experimentId: string,
  name?: string,
  smiles?: Blob,
  sdf?: Blob,
): CancelablePromise<LigandResponse> {
  const uploadLigand = {
    experiment_id: experimentId,
    name: name,
    smiles: smiles,
    sdf: sdf
  } as Body_upload_ligand_api_v1_objects_ligands_post;
  return LigandsService.uploadLigandApiV1ObjectsLigandsPost(uploadLigand);
}

export function deleteLigand(ligandId: string): CancelablePromise<any> {
  return LigandsService.deleteLigandApiV1ObjectsLigandsLigandIdDelete(ligandId);
}

export async function checkBiobuddyEnabled(): Promise<boolean> {
  const response = await BiobuddyService.checkBiobuddyEnabledApiV1BiobuddyCheckBiobuddyEnabledGet();
  return response.enabled;
}
