import json
from typing import Dict, Any, List

from nolabs.domain.experiment import ExperimentId
from nolabs.api_models.biobuddy import FunctionCall, FunctionParam, FunctionCallReturnData
from nolabs.modules.biobuddy.functions.base_function import BiobuddyFunction, FunctionParameterDefinition
from nolabs.modules.drug_discovery.services.target_file_management import TargetsFileManagement
from nolabs.infrastructure.settings import Settings

components = []
class GenerateWorkflowFunction(BiobuddyFunction):
    def __init__(self, settings: Settings):
        parameters = [
            FunctionParameterDefinition(name="workflow",
                                        type="string",
                                        required=True,
                                        description=f"Generate a JSON which would be used to construct a workflow "
                                                    f"graph. Components: {', '.join(component.name for component in components)}",
                                        items_type="string")
        ]
        super().__init__("create_workflow", "Generate a workflow function. Creates a JSON from which a workflow is "
                                            "constructed", parameters)
        self._settings = settings
        self._components = components

    def execute(self, experiment_id: ExperimentId, arguments: Dict[str, Any]) -> FunctionCall:
        return_json_string = arguments[self.parameters[0].name]
        print(f"Executing {self.name} with arguments {arguments}")

        workflow = json.loads(return_json_string)

        print("WORKFLOW:", workflow)

        return FunctionCall(function_name="create_workflow", parameters=[],
                            data=FunctionCallReturnData(files=workflow))
