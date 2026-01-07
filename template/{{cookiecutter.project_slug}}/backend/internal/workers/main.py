# Temporal Worker Main Entry Point
# ================================
# This is the main entry point for Temporal workers.
# Run with: python -m internal.workers.main
#
# Make sure Temporal server is running:
#   docker compose up temporal
#
# Environment variables:
#   TEMPORAL_HOST: Temporal server host (default: localhost:7233)
#   TEMPORAL_NAMESPACE: Temporal namespace (default: default)

import asyncio
import logging
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from temporalio.client import Client
from temporalio.worker import Worker

from internal.workers.workflows import (
    EmailNotificationWorkflow,
    DataProcessingWorkflow,
    ScheduledReportWorkflow,
)
from internal.workers.activities import (
    send_email_activity,
    process_data_activity,
    generate_report_activity,
    upload_to_s3_activity,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Start the Temporal worker."""
    host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "{{ cookiecutter.project_slug }}-tasks")
    
    logger.info(f"Connecting to Temporal at {host}")
    
    # Connect to Temporal
    client = await Client.connect(host, namespace=namespace)
    
    logger.info(f"Starting worker on task queue: {task_queue}")
    
    # Create worker with workflows and activities
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[
            EmailNotificationWorkflow,
            DataProcessingWorkflow,
            ScheduledReportWorkflow,
        ],
        activities=[
            send_email_activity,
            process_data_activity,
            generate_report_activity,
            upload_to_s3_activity,
        ],
    )
    
    logger.info("Worker started successfully!")
    logger.info("Press Ctrl+C to stop")
    
    # Run worker
    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped")
