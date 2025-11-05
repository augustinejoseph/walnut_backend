from django.urls import path
from .views import HealthView, WebhookTransactionView, TransactionRetrieveView

urlpatterns = [
    path("", HealthView.as_view(), name="health"),
    path(
        "v1/webhooks/transactions",
        WebhookTransactionView.as_view(),
        name="webhook_transactions",
    ),
    path(
        "v1/transactions/<str:transaction_id>",
        TransactionRetrieveView.as_view(),
        name="transaction_status",
    ),
]
