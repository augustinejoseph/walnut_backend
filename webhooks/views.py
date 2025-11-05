from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import IntegrityError, transaction as db_transaction
from .models import Transaction
from .serializers import TransactionCreateSerializer, TransactionSerializer
from .tasks import process_transaction_task


class HealthView(APIView):
    def get(self, request):
        return Response(
            {"status": "HEALTHY", "current_time": timezone.now().isoformat()}
        )


import logging
from django.db import transaction as db_transaction, IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import TransactionCreateSerializer
from .tasks import process_transaction_task

logger = logging.getLogger(__name__)


class WebhookTransactionView(APIView):
    """
    POST /v1/webhooks/transactions
    Accepts transaction webhooks, returns 202 immediately, and triggers background processing.
    Ensures idempotency and consistent logging.
    """

    def post(self, request):
        serializer = TransactionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        transaction_id = data["transaction_id"]

        enqueue_task, created_new = False, False

        try:
            with db_transaction.atomic():
                tx, created = Transaction.objects.get_or_create(
                    transaction_id=transaction_id,
                    defaults={
                        "source_account": data["source_account"],
                        "destination_account": data["destination_account"],
                        "amount": data["amount"],
                        "currency": data["currency"],
                        "status": Transaction.STATUS_RECEIVED,
                        "task_enqueued": True,
                    },
                )

                if created:
                    enqueue_task, created_new = True, True
                    logger.info(f"New transaction created | ID={transaction_id}")
                elif tx.status != Transaction.STATUS_PROCESSED and not tx.task_enqueued:
                    tx.task_enqueued = True
                    tx.save(update_fields=["task_enqueued"])
                    enqueue_task = True
                    logger.info(f"Re-queued existing transaction | ID={transaction_id}")
                else:
                    logger.warning(
                        f"Duplicate webhook ignored | ID={transaction_id} | Status={tx.status}"
                    )

        except IntegrityError:
            tx = Transaction.objects.get(transaction_id=transaction_id)
            if tx.status != Transaction.STATUS_PROCESSED and not tx.task_enqueued:
                tx.task_enqueued = True
                tx.save(update_fields=["task_enqueued"])
                enqueue_task = True
                logger.info(
                    f"Integrity recovery | Re-queued transaction {transaction_id}"
                )
            else:
                logger.warning(
                    f"Duplicate webhook ignored (IntegrityError) | ID={transaction_id}"
                )

        if enqueue_task:
            try:
                process_transaction_task(transaction_id)
                logger.info(f"Enqueued background task | ID={transaction_id}")
            except Exception as e:
                logger.error(
                    f"Failed to enqueue background task | ID={transaction_id} | Error={e}",
                    exc_info=True,
                )

        response_msg = (
            f"Transaction {transaction_id} accepted for processing"
            if created_new or enqueue_task
            else f"Duplicate transaction {transaction_id} ignored"
        )

        return Response({"message": response_msg}, status=status.HTTP_202_ACCEPTED)


class TransactionRetrieveView(APIView):
    """
    GET /v1/transactions/{transaction_id}
    Returns transaction details (for testing)
    """

    def get(self, request, transaction_id):
        try:
            tx = Transaction.objects.get(transaction_id=transaction_id)
        except Transaction.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TransactionSerializer(tx)
        return Response(serializer.data)
