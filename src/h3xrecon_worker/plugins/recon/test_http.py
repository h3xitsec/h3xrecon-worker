from typing import AsyncGenerator, Dict, Any
from h3xrecon_worker.plugins.base import ReconPlugin
from h3xrecon_core import *
from loguru import logger
import asyncio
import json
import os

class TestHTTP(ReconPlugin):
    @property
    def name(self) -> str:
        return os.path.splitext(os.path.basename(__file__))[0]

    async def execute(self, target: str, program_id: int = None, execution_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
        logger.info(f"Running {self.name} on {target}")
        command = f"""
            #!/bin/bash
            httpx -u {target} \
                -fr \
                -silent \
                -status-code \
                -content-length \
                -tech-detect \
                -threads 50 \
                -no-color \
                -json \
                -p 80-99,443-449,11443,8443-8449,9000-9003,8080-8089,8801-8810,3000,5000 \
                -efqdn \
                -tls-grab \
                -pa \
                -tls-probe \
                -pipeline \
                -http2 \
                -vhost \
                -bp \
                -ip \
                -cname \
                -asn \
                -random-agent
        """
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        
        async for output in self._read_subprocess_output(process):
            try:
                json_data = json.loads(output)
                yield json_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON output: {e}")

        await process.wait()
    
    async def process_output(self, output_msg: Dict[str, Any]):
        self.config = Config()
        self.db_manager = DatabaseManager(self.config.database.to_dict())
        self.qm = QueueManager(self.config.nats)
        logger.debug(f"Incoming message:\nObject Type: {type(output_msg)}\nObject:\n{json.dumps(output_msg, indent=4)}")
        if not await self.db_manager.check_domain_regex_match(output_msg.get('source').get('target'), output_msg.get('program_id')):
            logger.info(f"Domain {output_msg.get('source').get('target')} is not part of program {output_msg.get('program_id')}. Skipping processing.")
        else:
            logger.info(f"Domain {output_msg.get('source').get('target')} is part of program {output_msg.get('program_id')}. Sending to data processor.")
            url_msg = {
                "program_id": output_msg.get('program_id'),
                "data_type": "url",
                "data": [{
                    "url": output_msg.get('output', {}).get('url'),
                    "httpx_data": output_msg.get('output', {})
                }]
            }
            await self.qm.publish_message(subject="recon.data", stream="RECON_DATA", message=url_msg)
            # await self.nc.publish(output_msg.get('recon_data_queue', "recon.data"), json.dumps(url_msg).encode())
            domains_to_add = (output_msg.get('output', {}).get('body_domains', []) + 
                              output_msg.get('output', {}).get('body_fqdn', []) + 
                              output_msg.get('output', {}).get('tls', {}).get('subject_an', []))
            logger.debug(domains_to_add)
            for domain in domains_to_add:
                if domain:
                    domain_msg = {
                        "program_id": output_msg.get('program_id'),
                        "data_type": "domain",
                        "data": [domain]
                    }
                    await self.qm.publish_message(subject="recon.data", stream="RECON_DATA", message=domain_msg)

            service_msg = {
                "program_id": output_msg.get('program_id'),
                "data_type": "service",
                "data": [{
                    "ip": output_msg.get('output').get('host'),
                    "port": int(output_msg.get('output').get('port')),
                    "protocol": "tcp",
                    "service": output_msg.get('output').get('scheme')
                }]
            }
            await self.qm.publish_message(subject="recon.data", stream="RECON_DATA", message=service_msg)