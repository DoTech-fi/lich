# Temporal Workflow Examples
# ==========================
# Workflows define the orchestration logic for long-running processes.
# They are deterministic and can be replayed from history.
#
# Key concepts:
# - Workflows are classes decorated with @workflow.defn
# - The main method is decorated with @workflow.run
# - Use workflow.execute_activity() to call activities
# - Workflows should be deterministic (no random, no datetime.now())

from datetime import timedelta
from typing import List, Optional

from temporalio import workflow

# Import activity stubs (not the actual activities)
with workflow.unsafe.imports_passed_through():
    from internal.workers.activities import (
        SendEmailInput,
        ProcessDataInput,
        GenerateReportInput,
        UploadToS3Input,
    )


@workflow.defn
class EmailNotificationWorkflow:
    """
    Send email notifications with retry logic.
    
    Usage:
        result = await client.execute_workflow(
            EmailNotificationWorkflow.run,
            EmailNotificationInput(to="user@example.com", subject="Hello", body="..."),
            id="email-123",
            task_queue="tasks",
        )
    """
    
    @workflow.run
    async def run(self, input: "SendEmailInput") -> bool:
        """Execute the email notification workflow."""
        return await workflow.execute_activity(
            "send_email_activity",
            input,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=workflow.RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
            ),
        )


@workflow.defn
class DataProcessingWorkflow:
    """
    Process data in batches with progress tracking.
    
    This workflow demonstrates:
    - Batch processing
    - Progress updates via queries
    - Child activities
    """
    
    def __init__(self):
        self._progress = 0
        self._total = 0
    
    @workflow.query
    def get_progress(self) -> dict:
        """Return current progress."""
        return {
            "progress": self._progress,
            "total": self._total,
            "percentage": (self._progress / self._total * 100) if self._total > 0 else 0,
        }
    
    @workflow.run
    async def run(self, items: List[str]) -> dict:
        """Process items in batches."""
        self._total = len(items)
        results = []
        
        for i, item in enumerate(items):
            # Process each item
            result = await workflow.execute_activity(
                "process_data_activity",
                ProcessDataInput(data=item),
                start_to_close_timeout=timedelta(minutes=5),
            )
            results.append(result)
            self._progress = i + 1
        
        return {
            "processed": len(results),
            "results": results,
        }


@workflow.defn
class ScheduledReportWorkflow:
    """
    Generate and upload scheduled reports.
    
    This workflow demonstrates:
    - Multiple sequential activities
    - Error handling
    - Conditional logic
    """
    
    @workflow.run
    async def run(
        self,
        report_type: str,
        upload_to_s3: bool = True,
    ) -> dict:
        """Generate report and optionally upload to S3."""
        
        # Generate report
        report = await workflow.execute_activity(
            "generate_report_activity",
            GenerateReportInput(report_type=report_type),
            start_to_close_timeout=timedelta(minutes=10),
        )
        
        result = {
            "report_type": report_type,
            "generated_at": report["generated_at"],
            "file_path": report["file_path"],
        }
        
        # Upload to S3 if requested
        if upload_to_s3:
            s3_result = await workflow.execute_activity(
                "upload_to_s3_activity",
                UploadToS3Input(
                    file_path=report["file_path"],
                    bucket="reports",
                    key=f"reports/{report_type}/{report['generated_at']}.pdf",
                ),
                start_to_close_timeout=timedelta(minutes=5),
            )
            result["s3_url"] = s3_result["url"]
        
        return result
