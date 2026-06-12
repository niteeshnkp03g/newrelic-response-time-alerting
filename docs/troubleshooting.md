# Troubleshooting

## Slack Message Not Received

Verify:

- Slack Webhook URL
- Lambda Logs
- API Gateway Endpoint

---

## Condition Name Not Available

Verify:

- NEW_RELIC_API_KEY
- NEW_RELIC_ACCOUNT_ID
- POLICY_IDS

---

## Workflow Not Triggering

Verify:

- Policy linked to Workflow
- Alert condition active

---

## Lambda Timeout

Increase Lambda timeout to 30 seconds.