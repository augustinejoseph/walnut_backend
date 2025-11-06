# Django Webhook Processing Service

This project implements a robust webhook receiver built with **Django** and **PostgreSQL**.  
It accepts transaction webhooks from external payment processors (like RazorPay), responds quickly (under 500ms), and processes transactions asynchronously in the background.

---

## Features

- **Immediate acknowledgment:** Returns `202 Accepted` instantly for all incoming webhooks.
- **Asynchronous background processing:** Uses a simulated 30-second delay to mimic external API calls.
- **Idempotent handling:** Duplicate webhooks with the same `transaction_id` are safely ignored.
- **Persistent storage:** All transactions are stored in SQL with timestamps and status updates.
- **Structured logging:** Detailed logs for new, duplicate, and failed transactions.

---

## API Endpoints

### 1. Health Check
**METHOD : GET**  
Returns the current server status.

URL : {baseurl}

**Response:**
```json
{
  "status": "HEALTHY",
  "current_time": "2025-11-05T10:30:00Z"
}
```

### 2. Webhook
**METHOD : POST**  
Accepts POST requests from the payment providers.

URL : {baseurl}/v1/webhooks/transactions
**Payload:**
```json

  {
    "transaction_id": "tns_2025_10_06_04873829",
    "source_account": "acc_user_789",
    "destination_account": "acc_merchant_456",
    "amount": 1500,
    "currency": "INR"
  }

```
**Response:**

Intial call :
```json
{
  "message": "Transaction tns_2025_10_06_04843829 accepted for processing"
  "status" : 202
}
}
```

Duplicate call :
```json
{
  "message": "Duplicate transaction tns_2025_10_06_04873829 ignored"
  "status" : 202
}
```



### 3. Get Transaction Details
**METHOD : GET**  
Accepts GET requests to return transaction details.

URL : {baseurl}/v1/transactions/{transaction_id}

**Response:**

Success
```json
{
  "message": "Transaction tns_2025_10_06_04843829 accepted for processing"
  "status" : 202
}
```