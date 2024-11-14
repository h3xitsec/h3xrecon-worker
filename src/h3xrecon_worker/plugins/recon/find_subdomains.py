import os
from typing import Dict, Any, AsyncGenerator
from h3xrecon_worker.plugins.base import ReconPlugin
from h3xrecon_core import QueueManager


class FindSubdomainsPlugin(ReconPlugin):
    """
    Meta plugin that triggers multiple subdomain discovery tools
    """
    @property
    def name(self) -> str:
        return os.path.splitext(os.path.basename(__file__))[0]

    async def execute(self, target: str, program_id: int, execution_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute the meta plugin by dispatching multiple subdomain discovery jobs
        """
        self.program_id = program_id
        self.execution_id = execution_id
        self.qm = QueueManager()
        # List of subdomain discovery tools to trigger
        subdomain_tools = [
            "find_subdomains_subfinder",
            "find_subdomains_ctfr"
        ]
        
        # Send jobs for each tool
        for tool in subdomain_tools:
            await self.send_job(
                function_name=tool,
                target=target,
            )
            # Yield a status message for each dispatched job
            yield {}
    
    async def send_job(self, function_name: str, target: str, options: Dict[str, Any] = None) -> None:
        """
        Helper method to send a job to the worker queue
        """
        job_data = {
            "force": False,
            "function": function_name,
            "program_id": self.program_id,
            "params": {"target": target}
        }
        
        # Use the NATS client to publish the job
        await self.qm.publish_message(
            subject="function.execute",
            stream="FUNCTION_EXECUTE",
            message=job_data
        )