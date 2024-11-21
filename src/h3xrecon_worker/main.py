"""
Main entry point for the H3XRecon worker component.
"""

import asyncio
from loguru import logger
from h3xrecon_core.config import Config
from h3xrecon_worker.base import Worker
from h3xrecon_worker.__about__ import __version__
import sys

async def main():
    try:
        # Load configuration
        config = Config()
        config.setup_logging()
        logger.info(f"Starting H3XRecon worker... (v{__version__})")

        # Initialize and start worker
        worker = Worker(config)
        
        try:
            await worker.start()
            
            # Keep the worker running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down worker...")
            await worker.stop()
            
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Worker shutdown complete")

def run():
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())