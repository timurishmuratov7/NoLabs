__all__ = [
    'LocalisationJob'
]

from typing import List
from uuid import UUID

from mongoengine import ReferenceField, ListField, PULL, EmbeddedDocument, FloatField, EmbeddedDocumentListField, \
    UUIDField

from nolabs.exceptions import NoLabsException, ErrorCodes
from nolabs.refined.domain.models.common import Job, AminoAcid, LocalisationProbability


class LocalisationJobResult(EmbeddedDocument):
    """
    Not a domain object
    Currently used just to keep job outputs
    """
    amino_acid_id: UUID = UUIDField(required=True)
    cytosolic: float = FloatField(required=True)
    mitochondrial: float = FloatField(required=True)
    nuclear: float = FloatField(required=True)
    other: float = FloatField(required=True)
    extracellular: float = FloatField(required=True)


class LocalisationJob(Job):
    amino_acids: List[AminoAcid] = ListField(ReferenceField(AminoAcid, required=False, reverse_delete_rule=PULL))
    probabilities: List[LocalisationJobResult] = EmbeddedDocumentListField(LocalisationJobResult)

    def set_amino_acids(self, amino_acids: List[AminoAcid]):
        if not amino_acids:
            raise NoLabsException(ErrorCodes.invalid_job_input)

        self.amino_acids = amino_acids

    def clear_result(self):
        self.probabilities = []

    def set_result(self, amino_acid: AminoAcid, localisation: LocalisationProbability):
        if not self.amino_acids:
            raise NoLabsException(ErrorCodes.invalid_job_input)

        if amino_acid not in self.amino_acids:
            raise NoLabsException(ErrorCodes.invalid_aa_id)

        existing_result = [res for res in self.probabilities if res.amino_acid_id == amino_acid.id]
        if existing_result:
            localisation_result = existing_result[0]
            localisation_result.amino_acid_id = amino_acid.id
            localisation_result.cytosolic = localisation.cytosolic
            localisation_result.mitochondrial = localisation.mitochondrial
            localisation_result.nuclear = localisation.nuclear
            localisation_result.other = localisation.other
            localisation_result.extracellular = localisation.extracellular
        else:
            localisation_result = LocalisationJobResult(
                amino_acid_id=amino_acid.id,
                cytosolic=localisation.cytosolic,
                mitochondrial=localisation.mitochondrial,
                nuclear=localisation.nuclear,
                other=localisation.other,
                extracellular=localisation.extracellular,
            )
            self.probabilities.append(localisation_result)