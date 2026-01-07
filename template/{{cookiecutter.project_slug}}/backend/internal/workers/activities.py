# Temporal Activity Examples
# ==========================
# Activities are the building blocks of workflows.
# They contain the actual business logic that can have side effects.
#
# Key concepts:
# - Activities are functions decorated with @activity.defn
# - They can call external services, databases, APIs
# - They should be idempotent when possible
# - Use heartbeats for long-running activities

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from temporalio import activity

logger = logging.getLogger(__name__)


# ============================================
# Input Data Classes
# ============================================

@dataclass
class SendEmailInput:
    """Input for send_email_activity."""
    to: str
    subject: str
    body: str
    template: Optional[str] = None


@dataclass
class ProcessDataInput:
    """Input for process_data_activity."""
    data: str
    options: Optional[dict] = None


@dataclass
class GenerateReportInput:
    """Input for generate_report_activity."""
    report_type: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass
class UploadToS3Input:
    """Input for upload_to_s3_activity."""
    file_path: str
    bucket: str
    key: str


# ============================================
# Activity Implementations
# ============================================

@activity.defn
async def send_email_activity(input: SendEmailInput) -> bool:
    """
    Send an email notification.
    
    In production, replace with actual email service:
    - SendGrid, Mailgun, AWS SES, etc.
    """
    logger.info(f"Sending email to {input.to}: {input.subject}")
    
    # TODO: Implement actual email sending
    # Example with SendGrid:
    # import sendgrid
    # sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    # message = Mail(from_email='noreply@example.com', to_emails=input.to, ...)
    # sg.send(message)
    
    # Simulate success
    logger.info(f"Email sent successfully to {input.to}")
    return True


@activity.defn
async def process_data_activity(input: ProcessDataInput) -> dict:
    """
    Process a single data item.
    
    This is an example of a generic data processing activity.
    For long-running operations, use heartbeats.
    """
    logger.info(f"Processing data: {input.data[:50]}...")
    
    # Report heartbeat for long operations
    activity.heartbeat(f"Processing: {input.data[:20]}")
    
    # TODO: Implement actual processing logic
    # - Parse data
    # - Transform
    # - Validate
    # - Store results
    
    result = {
        "input": input.data,
        "processed_at": datetime.utcnow().isoformat(),
        "status": "completed",
    }
    
    logger.info(f"Data processed successfully")
    return result


@activity.defn
async def generate_report_activity(input: GenerateReportInput) -> dict:
    """
    Generate a report.
    
    This could generate PDF, Excel, CSV, etc.
    For long-running reports, use heartbeats.
    """
    logger.info(f"Generating {input.report_type} report")
    
    # Heartbeat during generation
    activity.heartbeat("Querying database...")
    
    # TODO: Implement actual report generation
    # - Query database
    # - Generate charts
    # - Create PDF/Excel
    
    activity.heartbeat("Building report...")
    
    file_path = f"/tmp/reports/{input.report_type}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    
    result = {
        "report_type": input.report_type,
        "generated_at": datetime.utcnow().isoformat(),
        "file_path": file_path,
    }
    
    logger.info(f"Report generated: {file_path}")
    return result


@activity.defn
async def upload_to_s3_activity(input: UploadToS3Input) -> dict:
    """
    Upload a file to S3.
    
    Uses boto3 to upload files to AWS S3.
    """
    logger.info(f"Uploading {input.file_path} to s3://{input.bucket}/{input.key}")
    
    # TODO: Implement actual S3 upload
    # import boto3
    # s3 = boto3.client('s3')
    # s3.upload_file(input.file_path, input.bucket, input.key)
    
    url = f"https://{input.bucket}.s3.amazonaws.com/{input.key}"
    
    logger.info(f"Upload complete: {url}")
    return {
        "bucket": input.bucket,
        "key": input.key,
        "url": url,
    }
