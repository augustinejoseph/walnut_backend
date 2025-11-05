from django.db import models
from django.utils import timezone
from decimal import Decimal


class Transaction(models.Model):
    STATUS_RECEIVED = "RECEIVED"
    STATUS_PROCESSING = "PROCESSING"
    STATUS_PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    STATUS_FAILED = "FAILED"
    STATUS_PROCESSED = "PROCESSED"

    STATUS_CHOICES = [
        (STATUS_RECEIVED, "Received"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_PENDING_CONFIRMATION, "Pending Confirmation"),
        (STATUS_FAILED, "Failed"),
        (STATUS_PROCESSED, "Processed"),
    ]

    transaction_id = models.CharField(max_length=128, unique=True)
    source_account = models.CharField(max_length=128)
    destination_account = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=10)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PROCESSING
    )
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    # ensure only one processing task gets queued per DB record
    task_enqueued = models.BooleanField(default=False)

    def mark_processing(self):
        self.status = self.STATUS_PROCESSING
        self.save(update_fields=["status"])

    def mark_pending(self):
        self.status = self.STATUS_PENDING_CONFIRMATION
        self.save(update_fields=["status"])

    def mark_failed(self):
        self.status = self.STATUS_FAILED
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])

    def mark_processed(self):
        self.status = self.STATUS_PROCESSED
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])
