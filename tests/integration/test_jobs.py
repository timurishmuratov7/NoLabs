import uuid
from typing import Type, List, Optional, Dict, Any

from asgiref.sync import async_to_sync
from pydantic import BaseModel

from integration.mixins import SeedComponentsMixin, SeedExperimentMixin, GraphTestMixin
from integration.setup import GlobalSetup
from nolabs.domain.models.common import Job, JobId, JobName
from nolabs.infrastructure.celery_app_factory import get_celery_app
from nolabs.infrastructure.settings import settings
from nolabs.workflow.core.component import Component, TOutput, TInput
from nolabs.workflow.core.flow import ComponentFlowHandler
from nolabs.workflow.core.graph import GraphExecutionNode
from nolabs.workflow.core.states import ControlStates
from nolabs.workflow.core.syncer import Syncer


class TestJobs(GlobalSetup,
               SeedComponentsMixin,
               SeedExperimentMixin,
               GraphTestMixin):
    async def test_should_successfully_run_long_running_job(self):
        celery = get_celery_app()

        def long_running_job_success(bind, job_id: uuid.UUID):
            async def _():
                job: Job = Job.objects.with_id(job_id)
                job.set_name(JobName("long_running_job_test_success"))
                await job.save()

            async_to_sync(_)()

        celery.task(long_running_job_success, name="long_running_job_test_success", bind=True, queue=settings.workflow_queue)

        j1_id = uuid.uuid4()
        j2_id = uuid.uuid4()

        class IO(BaseModel):
            a: int = 10

        class FlowHandler(ComponentFlowHandler):
            async def on_component_task(self, inp: IO) -> List[uuid.UUID]:
                job1 = Job.create(id=JobId(j1_id), name=JobName("hello 1"), component=self.component_id)
                job2 = Job.create(id=JobId(j2_id), name=JobName("hello 2"), component=self.component_id)
                await job1.save()
                await job2.save()

                return [job1.id, job2.id]

            async def on_job_task(self, job_id: uuid.UUID):
                j: Job = Job.objects.with_id(job_id)
                j.name = JobName("Changed")
                await j.save()
                await self.schedule_long_running(job_id=job_id, celery_task_name="long_running_job_test_success",
                                                 input={"job_id": job_id})

        class MockComponent(Component[IO, IO], ComponentFlowHandler):
            name = "a"

            @property
            def input_parameter_type(self) -> Type[TInput]:
                return IO

            @property
            def component_flow_type(self) -> Type["ComponentFlowHandler"]:
                return FlowHandler

            @property
            def output_parameter_type(self) -> Type[TOutput]:
                return IO

        # arrange
        experiment_id = uuid.uuid4()
        await self.seed_experiment(id=experiment_id)
        component = self.seed_component(experiment_id=experiment_id, component_type=MockComponent)
        graph = GraphExecutionNode(experiment_id=experiment_id)
        self.spin_up_celery()

        # act
        await graph.schedule(components=[component])
        scheduler = Syncer()
        await scheduler.sync_graph(experiment_id=experiment_id, wait=True)

        # assert
        job1 = Job.objects.get(id=j1_id)
        job2 = Job.objects.get(id=j2_id)

        self.assertEqual(await graph.get_component_node(component_id=component.id).get_state(), ControlStates.SUCCESS)
        self.assertEqual(job1.name.value, "long_running_job_test_success")
        self.assertEqual(job2.name.value, "long_running_job_test_success")

    async def test_should_fail_on_longrunning_fail(self):
        celery = get_celery_app()

        def long_running_job_test_failed(bind, job_id: uuid.UUID):
            async def _():
                raise ValueError("Hello")

            async_to_sync(_)()

        celery.task(long_running_job_test_failed, name="long_running_job_test_failed", bind=True, queue=settings.workflow_queue)

        j1_id = uuid.uuid4()
        j2_id = uuid.uuid4()

        class IO(BaseModel):
            a: int = 10

        class FlowHandler(ComponentFlowHandler):
            async def on_component_task(self, inp: IO) -> List[uuid.UUID]:
                job1 = Job.create(id=JobId(j1_id), name=JobName("hello 1"), component=self.component_id)
                job2 = Job.create(id=JobId(j2_id), name=JobName("hello 2"), component=self.component_id)
                await job1.save()
                await job2.save()

                return [job1.id, job2.id]

            async def on_job_task(self, job_id: uuid.UUID):
                j: Job = Job.objects.with_id(job_id)
                j.name = JobName("Changed")
                await j.save()
                await self.schedule_long_running(job_id=job_id, celery_task_name="long_running_job_test_failed",
                                                 input={"job_id": job_id})

        class MockComponent(Component[IO, IO], ComponentFlowHandler):
            name = "a"

            @property
            def input_parameter_type(self) -> Type[TInput]:
                return IO

            @property
            def component_flow_type(self) -> Type["ComponentFlowHandler"]:
                return FlowHandler

            @property
            def output_parameter_type(self) -> Type[TOutput]:
                return IO

        # arrange
        experiment_id = uuid.uuid4()
        await self.seed_experiment(id=experiment_id)
        component = self.seed_component(experiment_id=experiment_id, component_type=MockComponent)
        graph = GraphExecutionNode(experiment_id=experiment_id)
        self.spin_up_celery()

        # act
        await graph.schedule(components=[component])
        scheduler = Syncer()
        await scheduler.sync_graph(experiment_id=experiment_id, wait=True)

        # assert
        self.assertEqual(await graph.get_component_node(component_id=component.id).get_state(), ControlStates.FAILURE)
        self.assertEqual(await graph.get_job_node(component_id=component.id, job_id=j1_id).get_message(),
                         "Hello")
        self.assertEqual(await graph.get_job_node(component_id=component.id,
                                                        job_id=j2_id).get_message(),
                         "Hello")

    async def test_should_fail_on_completed_failure(self):
        celery = get_celery_app()

        def long_running_job_test_success(bind, job_id: uuid.UUID):
            print('ok')

        celery.task(long_running_job_test_success, name="long_running_job_test_success", bind=True, queue=settings.workflow_queue)

        j1_id = uuid.uuid4()
        j2_id = uuid.uuid4()

        class IO(BaseModel):
            a: int = 10

        class FlowHandler(ComponentFlowHandler):
            async def on_component_task(self, inp: IO) -> List[uuid.UUID]:
                job1 = Job.create(id=JobId(j1_id), name=JobName("hello 1"), component=self.component_id)
                job2 = Job.create(id=JobId(j2_id), name=JobName("hello 2"), component=self.component_id)
                await job1.save()
                await job2.save()

                return [job1.id, job2.id]

            async def on_job_task(self, job_id: uuid.UUID):
                j: Job = Job.objects.with_id(job_id)
                j.name = JobName("Changed")
                await j.save()
                await self.schedule_long_running(job_id=job_id, celery_task_name="long_running_job_test_success",
                                                 input={"job_id": job_id})

            async def on_job_completion(self, job_id: uuid.UUID, long_running_output: Optional[Dict[str, Any]]):
                raise ValueError("Failed completion")

        class MockComponent(Component[IO, IO], ComponentFlowHandler):
            name = "a"

            @property
            def input_parameter_type(self) -> Type[TInput]:
                return IO

            @property
            def component_flow_type(self) -> Type["ComponentFlowHandler"]:
                return FlowHandler

            @property
            def output_parameter_type(self) -> Type[TOutput]:
                return IO

        # arrange
        experiment_id = uuid.uuid4()
        await self.seed_experiment(id=experiment_id)
        component = self.seed_component(experiment_id=experiment_id, component_type=MockComponent)
        graph = GraphExecutionNode(experiment_id=experiment_id)
        self.spin_up_celery()

        # act
        await graph.schedule(components=[component])
        scheduler = Syncer()
        await scheduler.sync_graph(experiment_id=experiment_id, wait=True)

        # assert
        self.assertEqual(await graph.get_component_node(component_id=component.id).get_state(), ControlStates.FAILURE)
        self.assertEqual(await graph.get_job_node(component_id=component.id, job_id=j1_id).get_message(),
                         "Failed completion")
        self.assertEqual(await graph.get_job_node(component_id=component.id,
                                                        job_id=j2_id).get_message(),
                         "Failed completion")