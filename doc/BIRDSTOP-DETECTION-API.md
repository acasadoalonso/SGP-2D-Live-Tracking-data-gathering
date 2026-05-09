# Birdstop Detection API — Specification v1.0

---

## Overview

**Base URL:** `http://3.22.63.131/v1`  
**Protocol:** HTTP  
**Format:** JSON (`application/json`)

---

## Authentication

Every request must include your API key in an HTTP header. Keys are issued per integration and can be rotated by contacting Birdstop.

```
X-API-Key: bsdk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Keys are prefixed `bsdk_live_` for production. Treat your key like a password — never expose it in client-side code.

---

## Endpoint: `GET /detections`

Returns a list of detection events. Filter by type, site, time range, and confidence.

### Request

```
GET http://3.22.63.131/v1/detections
X-API-Key: bsdk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `type` | string | No | `bird` only at this time. |
| `site_id` | string | No | Filter to a specific beacon/site (e.g. `BCN1`, `LCG2`). |
| `from` | ISO 8601 | No | Return events at or after this UTC timestamp. |
| `to` | ISO 8601 | No | Return events at or before this UTC timestamp. |
| `min_confidence` | float | No | Minimum confidence score (0.0–1.0). Default: `0.0`. |
| `limit` | integer | No | Max results per page (1–500). Default: `100`. |

### Example Request

```
GET http://3.22.63.131/v1/detections?type=bird&from=2025-06-01T00:00:00Z&min_confidence=0.8&limit=50
X-API-Key: bsdk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Response

```json
{
  "data": [
    {
      "id":          "bird_BCN1_1042",
      "type":        "bird",
      "site_id":     "BCN1",
      "site_name":   "BCN1",
      "timestamp":   "2025-06-12T14:22:05",
      "latitude":    41.3096,
      "longitude":   2.0902,
      "altitude_m":  45.2,
      "confidence":  0.8,
      "sensor":      "BCN1",
      "track_id":    null,
      "metadata": {
        "track_deg":         182.5,
        "gs_knts":           12.3,
        "distance_from_mic": 38.1,
        "category":          "Bird"
      }
    }
  ],
  "count":       50,
  "total":       1842,
  "next_cursor": null
}
```

### Response Fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique detection event identifier. |
| `type` | string | `bird`. |
| `site_id` | string | Beacon ID where the detection occurred (e.g. `BCN1`). |
| `site_name` | string | Human-readable site name. |
| `timestamp` | ISO 8601 | UTC time of the detection. |
| `latitude` | float | WGS-84 latitude. |
| `longitude` | float | WGS-84 longitude. |
| `altitude_m` | float | Altitude in meters AGL. `null` if unavailable. |
| `confidence` | float | Model confidence: 0.0 (low) to 1.0 (high). |
| `sensor` | string | Sensor/beacon ID that produced the detection. |
| `track_id` | string | Flight ID if available. `null` if not present. |
| `metadata` | object | Additional sensor fields: `track_deg`, `gs_knts`, `distance_from_mic`, `category`. |
| `count` | integer | Records returned in this response. |
| `total` | integer | Total matching records. |
| `next_cursor` | string | Always `null` in v1 — pagination coming in a future release. |

---

## Errors

| HTTP | Code | Meaning |
|---|---|---|
| `401` | `unauthorized` | Missing or invalid API key. |
| `422` | `invalid_params` | A query parameter failed validation. |
| `500` | `server_error` | Server error. Retry with exponential backoff. |

```json
{
  "error": {
    "code":    "invalid_params",
    "message": "Parameter 'min_confidence' must be between 0.0 and 1.0.",
    "param":   "min_confidence"
  }
}
```

---

## Rate Limits

| Req / Minute | Req / Day |
|---|---|
| 12 | 10,000 |

---

## Quick Start

**curl**
```bash
curl -G "http://3.22.63.131/v1/detections" \
  -H "X-API-Key: bsdk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  --data-urlencode "type=bird" \
  --data-urlencode "from=2025-06-01T00:00:00Z" \
  --data-urlencode "min_confidence=0.8" \
  --data-urlencode "limit=25"
```

**Python**
```python
import requests

resp = requests.get(
    "http://3.22.63.131/v1/detections",
    headers={"X-API-Key": "bsdk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"},
    params={
        "type": "bird",
        "from": "2025-06-01T00:00:00Z",
        "min_confidence": 0.8,
        "limit": 25,
    }
)
events = resp.json()["data"]
```

---

## Keys & Support

To request a key or rotate one, contact **douglas.muhlbauer@birdstop.io**.