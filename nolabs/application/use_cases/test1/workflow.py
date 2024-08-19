import uuid
from typing import Type, Optional, List, Any, ClassVar

from airflow.utils.context import Context
from pydantic import BaseModel

from nolabs.application.workflow.component import Component, TOutput, TInput
from nolabs.application.workflow.operators import SetupOperator, JobOperator, OutputOperator
from nolabs.domain.models.common import Job, JobInputError, JobId, JobName, Experiment


class Test1Input(BaseModel):
    x: int
    y: int = 10


class Test1Output(BaseModel):
    x: int
    y: int


class Test1Job(Job):

    def result_valid(self) -> bool:
        return True

    def _input_errors(self) -> List[JobInputError]:
        return []


class Test1SetupOperator(SetupOperator):

    async def execute_async(self, context: Context) -> List[str]:
        component: Optional[Test1Component] = Component.get(self.component_id)
        experiment: Experiment = Experiment.objects.with_id(component.experiment_id)

        job_ids = []

        for i in range(component.input_value.x):
            job = Test1Job(id=JobId(uuid.uuid4()), name=JobName('test'), experiment=experiment)
            await job.save()

            job_ids.append(job.iid)

        return self.serialize_job_ids(job_ids)


class Test1JobOperator(JobOperator):

    async def execute_async(self, context: Context) -> Any:
        self.log.info(f'Hello there, job id is {self.job_id}')


class Test1OutputOperator(OutputOperator):
    async def execute_async(self, context: Context) -> Any:
        self.setup_output(Test1Output(x=15, y=35))


class Test1Component(Component[Test1Input, Test1Output]):
    name: ClassVar[str] = 'test1'
    description: ClassVar[str] = 'test1 desc'

    @property
    def input_parameter_type(cls) -> Type[TInput]:
        return Test1Input

    @property
    def output_parameter_type(cls) -> Type[TOutput]:
        return Test1Output

    @property
    def setup_operator_type(self) -> Type['SetupOperator']:
        return Test1SetupOperator

    @property
    def job_operator_type(self) -> Optional[Type['JobOperator']]:
        return Test1JobOperator

    @property
    def output_operator_type(self) -> Type['OutputOperator']:
        return Test1OutputOperator
