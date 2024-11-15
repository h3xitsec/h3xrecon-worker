from typing import AsyncGenerator, Dict, Any
from h3xrecon_worker.plugins.base import ReconPlugin
from h3xrecon_core import *
from loguru import logger
import asyncio
import json
import os
class FindSubdomainsCTFR(ReconPlugin):
    @property
    def name(self) -> str:
        return os.path.splitext(os.path.basename(__file__))[0]

    async def execute(self, target: str, program_id: int = None, execution_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
        logger.info(f"Running {self.name} on {target}")
        command = f"""
            #!/bin/bash
            python /opt/ctfr/ctfr.py -d {target} -o /tmp/ctfr.log > /dev/null 2>&1
            cat /tmp/ctfr.log | grep -Ev ".*\\*.*" | sort -u
            rm /tmp/ctfr.log
        """
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        async for output in self._read_subprocess_output(process):
            yield {"subdomain": [output]}

        await process.wait()
    
    async def process_output(self, output_msg: Dict[str, Any]):
        self.config = Config()
        self.db_manager = DatabaseManager(self.config.database.to_dict())
        self.qm = QueueManager(self.config.nats)
        domain_msg = {
            "program_id": output_msg.get('program_id'),
            "data_type": "domain",
            "in_scope": output_msg.get('in_scope'),
            "data": output_msg.get('output', {}).get('subdomain')
        }
        await self.qm.publish_message(subject="recon.data", stream="RECON_DATA", message=domain_msg)