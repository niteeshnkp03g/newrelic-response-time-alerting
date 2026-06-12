# Architecture

## Flow

New Relic APM
→ Alert Condition
→ Workflow
→ API Gateway
→ AWS Lambda
→ Slack Channel

## Why Lambda?

Lambda enriches alerts before sending to Slack.

It fetches:

- Condition Name
- Threshold
- Entity Name
- Chart URL
- Issue URL

using New Relic GraphQL APIs.

## Why API Gateway?

API Gateway acts as public endpoint for New Relic Webhooks.

## Slack Notifications

The final message contains:

- Alert Name
- Entity
- Threshold
- Opened Time
- Closed Time
- Issue URL