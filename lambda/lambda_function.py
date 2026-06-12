import json
import urllib.request
import urllib.error
import os
from datetime import datetime, timezone, timedelta

NEW_RELIC_API_KEY = os.environ.get("NEW_RELIC_API_KEY", "")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
POLICY_IDS = os.environ.get("POLICY_IDS", "").split(",")
NEW_RELIC_ACCOUNT_ID = os.environ.get("NEW_RELIC_ACCOUNT_ID", "")

QUIET_HOURS_START = os.environ.get("QUIET_HOURS_START", "00:00")
QUIET_HOURS_END = os.environ.get("QUIET_HOURS_END", "06:00")

# -----------------------------
# NEW RELIC - POLICY SEARCH
# -----------------------------
def fetch_nrql_conditions(api_key, policy_id):
    if not NEW_RELIC_ACCOUNT_ID:
        print("❌ NEW_RELIC_ACCOUNT_ID missing")
        return []

    try:
        account_id_int = int(NEW_RELIC_ACCOUNT_ID)
        policy_id_int = int(policy_id.strip())
    except Exception as e:
        print("❌ Policy/account parsing error:", str(e))
        return []

    url = "https://api.newrelic.com/graphql"

    query = f"""
    {{
      actor {{
        account(id: {account_id_int}) {{
          alerts {{
            nrqlConditionsSearch(searchCriteria: {{policyId: {policy_id_int}}}) {{
              nrqlConditions {{
                id
                name
                terms {{
                  operator
                  threshold
                  priority
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """

    req = urllib.request.Request(
        url,
        data=json.dumps({"query": query}).encode(),
        headers={
            "API-Key": api_key,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        resp = urllib.request.urlopen(req, timeout=12)
        data = json.loads(resp.read().decode())

        conditions = (
            data.get("data", {})
            .get("actor", {})
            .get("account", {})
            .get("alerts", {})
            .get("nrqlConditionsSearch", {})
            .get("nrqlConditions", [])
        )

        print(f"✅ Fetched {len(conditions)} conditions for policy {policy_id}")
        return conditions

    except urllib.error.HTTPError as e:
        print("❌ HTTP Error in fetch_nrql_conditions:", e.code, e.reason)
        return []

    except urllib.error.URLError as e:
        print("❌ URL Error in fetch_nrql_conditions:", str(e))
        return []

    except Exception as e:
        print("❌ Unexpected Error in fetch_nrql_conditions:", str(e))
        return []

# -----------------------------
# NEW RELIC - DIRECT FETCH
# -----------------------------
def fetch_condition_by_id_direct(api_key, condition_id):
    if not NEW_RELIC_ACCOUNT_ID:
        print("❌ NEW_RELIC_ACCOUNT_ID missing")
        return None

    try:
        acc_id = int(NEW_RELIC_ACCOUNT_ID)
        cond_id = int(str(condition_id).strip())
    except Exception as e:
        print("❌ Condition/account parsing error:", str(e))
        return None

    url = "https://api.newrelic.com/graphql"

    query = f"""
    {{
      actor {{
        account(id: {acc_id}) {{
          alerts {{
            nrqlCondition(id: {cond_id}) {{
              id
              name
              terms {{
                operator
                threshold
                priority
              }}
            }}
          }}
        }}
      }}
    }}
    """

    req = urllib.request.Request(
        url,
        data=json.dumps({"query": query}).encode(),
        headers={
            "API-Key": api_key,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        resp = urllib.request.urlopen(req, timeout=12)
        data = json.loads(resp.read().decode())

        condition = (
            data.get("data", {})
            .get("actor", {})
            .get("account", {})
            .get("alerts", {})
            .get("nrqlCondition")
        )

        print("✅ Direct condition lookup successful")
        return condition

    except urllib.error.HTTPError as e:
        print("❌ HTTP Error in fetch_condition_by_id_direct:", e.code, e.reason)
        return None

    except urllib.error.URLError as e:
        print("❌ URL Error in fetch_condition_by_id_direct:", str(e))
        return None

    except Exception as e:
        print("❌ Unexpected Error in fetch_condition_by_id_direct:", str(e))
        return None

# -----------------------------
# SLACK
# -----------------------------
def send_to_slack(payload):
    try:
        req = urllib.request.Request(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )

        urllib.request.urlopen(req, timeout=8)
        print("✅ Sent to Slack")

    except Exception as e:
        print("❌ Slack error:", str(e))

# -----------------------------
# TIME
# -----------------------------
def convert_timestamp_to_ist(ts):
    if not ts or ts == "N/A":
        return "N/A"

    try:
        dt = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)

        return (
            dt + timedelta(hours=5, minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S IST")

    except Exception as e:
        print("❌ Timestamp conversion error:", str(e))
        return "N/A"

def is_within_quiet_hours(opened_time_str):
    try:
        if not opened_time_str or opened_time_str == "N/A":
            return False

        dt = datetime.strptime(
            opened_time_str,
            "%Y-%m-%d %H:%M:%S IST"
        )

        start = datetime.strptime(
            QUIET_HOURS_START,
            "%H:%M"
        ).time()

        end = datetime.strptime(
            QUIET_HOURS_END,
            "%H:%M"
        ).time()

        t = dt.time()

        if start < end:
            return start <= t < end

        return t >= start or t < end

    except Exception as e:
        print("❌ Quiet hours parsing error:", str(e))
        return False

# -----------------------------
# PARSING HELPERS
# -----------------------------
def lookup_condition(condition_id):
    print("🔍 lookup_condition called with:", condition_id)

    if not condition_id:
        print("❌ condition_id missing")
        return "Condition name not available", "N/A"

    cond = fetch_condition_by_id_direct(
        NEW_RELIC_API_KEY,
        condition_id
    )

    # Fallback search
    if not cond:
        print("⚠️ Direct lookup failed, trying policy search")

        for pid in POLICY_IDS:
            conditions = fetch_nrql_conditions(
                NEW_RELIC_API_KEY,
                pid
            )

            for c in conditions:
                if str(c.get("id")) == str(condition_id):
                    cond = c
                    break

            if cond:
                break

    print("📌 Condition lookup result:", cond)

    if cond:
        terms = cond.get("terms", [])

        crit = (
            next(
                (t for t in terms if t.get("priority") == "CRITICAL"),
                terms[0]
            )
            if terms else {}
        )

        threshold = (
            f"{crit.get('operator', '')} "
            f"{crit.get('threshold', '')} Milliseconds"
            if crit else "N/A"
        )

        return (
            cond.get("name", "Condition name not available"),
            threshold
        )

    return "Condition name not available", "N/A"

# -----------------------------
# LAMBDA HANDLER
# -----------------------------
def lambda_handler(event, context):

    body = event.get("body", event)

    if isinstance(body, str):
        body = json.loads(body)

    print("========== FULL PAYLOAD ==========")
    print(json.dumps(body, indent=2))

    attachments = body.get("attachments", [])

    fields = (
        attachments[0].get("fields", [])
        if attachments else []
    )

    text = body.get("text", "Alert")

    # Improved payload parsing
    condition_id = (
        body.get("conditionId")
        or body.get("condition_id")
        or body.get("data", {}).get("conditionId")
    )

    print("📌 condition_id:", condition_id)

    entity = "Entity name not available"
    issue_link = "N/A"
    raw_chart_url = None

    for f in fields:
        title = str(f.get("title", "")).lower()
        value = f.get("value", "")

        if "entity" in title and value:
            entity = value

        elif "more details" in title:
            issue_link = value

        elif "chart" in title:
            if (
                value
                and "Not Available" not in value
                and "|" in value
            ):
                raw_chart_url = (
                    value.split('|')[0]
                    .replace('<', '')
                    .strip()
                )

    # Additional fallback entity parsing
    if entity == "Entity name not available":
        try:
            entity = (
                body.get("targets", [{}])[0]
                .get("name", entity)
            )
        except Exception:
            pass

    condition_name, threshold = lookup_condition(condition_id)

    opened_ist = convert_timestamp_to_ist(
        body.get("createdAt")
    )

    closed_raw = body.get("closedAt")

    closed_ist = (
        convert_timestamp_to_ist(closed_raw)
        if closed_raw != "N/A"
        else "N/A"
    )

    if is_within_quiet_hours(opened_ist):
        print("🔕 Quiet hours active")
        return {
            "statusCode": 200,
            "body": "Quiet hours"
        }

    slack_text = (
        f"{text}\n\n"
        f":loudspeaker: *Title:* `{condition_name}`\n"
        f":clipboard: *Entity:* `{entity}`\n"
        f":chart_with_upwards_trend: *Threshold:* `{threshold}`\n"
        f":clock3: *Opened (IST):* `{opened_ist}`\n"
    )

    if "RESOLVED" in text.upper() and closed_ist != "N/A":
        slack_text += (
            f":ballot_box_with_check: "
            f"*Closed (IST):* `{closed_ist}`\n"
        )

    slack_text += (
        f"\n:link: *More Details:* {issue_link}"
    )

    slack_payload = {
        "text": slack_text
    }

    # Visual Image Section
    if raw_chart_url:
        slack_payload["attachments"] = [
            {
                "image_url": raw_chart_url,
                "color": (
                    "#ff0000"
                    if "CRITICAL" in text.upper()
                    else "#36a64f"
                )
            }
        ]

    send_to_slack(slack_payload)

    return {
        "statusCode": 200,
        "body": "OK"
    }