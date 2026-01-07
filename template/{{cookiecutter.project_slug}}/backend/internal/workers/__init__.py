# Temporal Workers Package
# ========================
# This package contains Temporal workflows and activities.
#
# Quick start:
#   1. Start Temporal server: docker compose up temporal
#   2. Start worker: python -m internal.workers.main
#   3. Execute workflow from your app code

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
    SendEmailInput,
    ProcessDataInput,
    GenerateReportInput,
    UploadToS3Input,
)

__all__ = [
    # Workflows
    "EmailNotificationWorkflow",
    "DataProcessingWorkflow",
    "ScheduledReportWorkflow",
    # Activities
    "send_email_activity",
    "process_data_activity",
    "generate_report_activity",
    "upload_to_s3_activity",
    # Input types
    "SendEmailInput",
    "ProcessDataInput",
    "GenerateReportInput",
    "UploadToS3Input",
]
