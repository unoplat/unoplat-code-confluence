from temporalio import workflow
from typing import Dict, Any

@workflow.defn
class DraftWorkflow:
    @workflow.run
    async def run(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        # This is where you'll implement the workflow logic
        # For now, we'll just return the configuration
        return {
            "status": "completed",
            "configuration": configuration
        } 