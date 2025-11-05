from celery import shared_task
import time
from django.db import transaction as db_transaction
from .models import Transaction


# @shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_transaction_task(self, transaction_id):
    try:
        tx = Transaction.objects.get(transaction_id=transaction_id)
    except Transaction.DoesNotExist:
        return "not_found"

    # Skip if already finalized
    if tx.status in [Transaction.STATUS_PROCESSED, Transaction.STATUS_FAILED]:
        return "already_finalized"

    # Step 1: Mark as PROCESSING
    tx.mark_processing()
    time.sleep(10)  # simulate validation step

    # Step 2: Simulate waiting for external confirmation
    tx.mark_pending()
    time.sleep(10)

    # Step 3: Simulate success/failure outcome
    try:
        # Example: fake random outcome or success
        # raise Exception("Fake failure")  # Uncomment to test failure
        time.sleep(10)
        tx.mark_processed()
        return "processed"
    except Exception:
        tx.mark_failed()
        raise
