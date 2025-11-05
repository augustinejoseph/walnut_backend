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
**GET /**  
Returns the current server status.

**Response:**
```json
{
  "status": "HEALTHY",
  "current_time": "2025-11-05T10:30:00Z"
}
```