import {defineStore} from "pinia";
import {Notify} from "quasar";
import {ErrorCodes} from "src/api/errorTypes";
import {obtainErrorResponse} from "src/api/errorWrapper";
import {Job, InferenceRequest} from "src/features/aminoAcid/types";
import {AminoAcid} from "src/features/aminoAcid/localisation/types";
import {
  OpenAPI,
  LocalisationService,
  ProteinsService,
  JobsACommonControllerForJobsManagementService, ProteinResponse, GeneOntologyService
} from "../../../refinedApi/client";
import apiConstants from "../../../api/constants";

OpenAPI.BASE = apiConstants.hostname;

const useLocalisationStore = defineStore("localisation", {
  actions: {
    async setupJob(experimentId: string, request: InferenceRequest){
      let proteins: ProteinResponse[] = [];
      for(const fasta of request.fastas){
        const protein = await ProteinsService.uploadProteinApiV1ObjectsProteinsPost({
          experiment_id: experimentId,
          name: fasta.name,
          fasta: fasta
        });
        proteins.push(protein);
      }

      await LocalisationService.setupJobApiV1LocalisationJobsPost(
        {
          experiment_id: experimentId,
          job_id: request.jobId,
          job_name: request.jobName,
          protein_ids: proteins.map(p => p.id)
        }
      );
    },
    async inference(request: InferenceRequest): Promise<{
      job: Job<AminoAcid> | null,
      errors: string[]
    }> {
      const job = await LocalisationService.getJobApiV1LocalisationJobsJobIdGet(request.jobId!);

      await this.setupJob(job.experiment_id, request);

      const errorResponse = obtainErrorResponse(job);
      if (errorResponse) {
        for (const error of errorResponse.errors) {
          Notify.create({
            type: "negative",
            closeBtn: 'Close',
            message: error
          });
        }
        return {job: null, errors: errorResponse.errors};
      }

      const proteins = await ProteinsService.searchProteinsApiV1ObjectsProteinsSearchPost({
        ids: job.protein_ids
      });

      return {
        job: {
          id: job.job_id,
          name: job.job_name,
          aminoAcids: proteins.map(p => {
            return {
              name: p.name,
              sequence: p.fasta_content!,
              cytosolicProteins: p.localisation!.cytosolic,
              mitochondialProteins: p.localisation!.mitochondrial,
              nuclearProteins: p.localisation!.nuclear,
              otherProteins: p.localisation!.other,
              extracellularSecretedProteins: p.localisation!.extracellular
            };
          }),
          properties: {
            fastas: request.fastas
          }
        },
        errors: []
      };
    },
    async getJob(jobId: string): Promise<{
      job: Job<AminoAcid> | null,
      errors: string[]
    }> {
      const response = await LocalisationService.getJobApiV1LocalisationJobsJobIdGet(jobId);
      const errorResponse = obtainErrorResponse(response);
      if (errorResponse) {
        if (errorResponse.error_code === ErrorCodes.job_not_found) {
          return {
            job: {
              id: jobId,
              name: "New job",
              aminoAcids: [],
              properties: {
                fastas: []
              }
            }, errors: []
          };
        } else {
          Notify.create({
            type: "negative",
            message: errorResponse.errors[0]
          });
        }

        return {job: null, errors: errorResponse.errors};
      }

      const proteins = await ProteinsService.searchProteinsApiV1ObjectsProteinsSearchPost({
        ids: response.protein_ids
      });

      return {
        job: {
          id: response.job_id,
          name: response.job_name,
          aminoAcids: proteins.map(p => {
            return {
              name: p.name,
              sequence: p.fasta_content!,
              cytosolicProteins: p.localisation!.cytosolic,
              mitochondialProteins: p.localisation!.mitochondrial,
              nuclearProteins: p.localisation!.nuclear,
              otherProteins: p.localisation!.other,
              extracellularSecretedProteins: p.localisation!.extracellular
            };
          }),
          properties: {
            fastas: proteins.map(p =>
              new File([new Blob([p.fasta_content!])], p.fasta_name)
            )
          }
        }, errors: []
      };
    },
    async changeJobName(jobId: string, newName: string) {
      await JobsACommonControllerForJobsManagementService.updateApiV1JobsJobsJobIdPatch(
        jobId,
        {
          job_name: newName
        }
      );
    },
  }
});

export default useLocalisationStore;
