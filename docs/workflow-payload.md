# New Relic Workflow Payload

```json
{
  "text": "{{#if issueClosedAtUtc}}✅ RESOLVED - Response Time Normalized{{else}}🚨 CRITICAL - Response Time Threshold Crossed{{/if}}",

  "conditionId": "{{#if accumulations.conditionFamilyId.[0]}}{{accumulations.conditionFamilyId.[0]}}{{else if accumulations.tag.nr.alerts.conditionId.[0]}}{{accumulations.tag.nr.alerts.conditionId.[0]}}{{else}}N/A{{/if}}",

  "conditionName": "{{#if accumulations.conditionName.[0]}}{{accumulations.conditionName.[0]}}{{else}}Response Time{{/if}}",

  "createdAt": "{{createdAt}}",

  "closedAt": "{{#if closedAt}}{{closedAt}}{{else}}N/A{{/if}}",

  "attachments": [
    {
      "fields": [
        {
          "title": "📋 Entity Details",
          "value": "{{#if accumulations.metadata_entity_name.[0]}}{{accumulations.metadata_entity_name.[0]}}{{else}}N/A{{/if}}",
          "short": false
        },
        {
          "title": "☞ More Details",
          "value": "{{#if issuePageUrl}}<{{issuePageUrl}}|View Issue>{{else}}N/A{{/if}}",
          "short": false
        },
        {
          "title": "🖼️ Chart",
          "value": "{{#if violationChartUrl}}<{{violationChartUrl}}|View Chart>{{else}}Not Available{{/if}}",
          "short": false
        },
        {
          "title": "📅 Opened / Closed",
          "value": "Opened: {{createdAt}}\nClosed: {{#if closedAt}}{{closedAt}}{{else}}N/A{{/if}}",
          "short": false
        }
      ]
    }
  ]
}
```