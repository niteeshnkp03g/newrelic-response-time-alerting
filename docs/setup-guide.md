# Setup Guide

## 1. Create Slack Channel

Create a dedicated Slack channel.

Example:

production-alerts

---

## 2. Create Slack Incoming Webhook

Slack → Apps → Incoming Webhooks

Generate webhook URL.

Save it for Lambda environment variables.

---

## 3. Create New Relic Policy

Alerts & AI → Policies

Create:

Response Time Monitoring Policy

---

## 4. Create NRQL Condition

```sql
SELECT average(convert(apm.service.transaction.duration, unit, 'ms'))
AS 'Response time (ms)'
FROM Metric
WHERE entity.name = 'service_name'
```

Set threshold:

Critical > 2000 ms

---

## 5. Create Webhook Destination

Alerts & AI → Destinations

Type: Webhook

Endpoint:
API Gateway URL

---

## 6. Create Workflow

Link Policy with Destination.

Configure custom JSON payload.

---

## 7. Deploy Lambda

Upload lambda_function.py

Add environment variables.

---

## 8. Create API Gateway

Method: POST

Integration: Lambda

---

## 9. Testing

Trigger alert.

Verify Slack notification.