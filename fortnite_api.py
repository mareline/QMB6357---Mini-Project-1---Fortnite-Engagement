"""
fortnite_api.py - a small client for Epic's public Fortnite Data API that stays within its rate limit.

Official spec (read before coding): https://api.fortnite.com/ecosystem/v1/docs/openapi.yaml
(the Swagger page is https://api.fortnite.com/ecosystem/v1/docs/).

Staying within the rate limit (Epic's spec: "429: Rate limit exceeded. Please try again later."):
  * a short pause between every request (DELAY_SECONDS)
  * retry with exponential backoff on 429 (rate limit) and 5xx server errors,
    honouring the Retry-After header when the server sends one
  * a hard cap on the total number of HTTP requests per run (MAX_REQUESTS)
  * a generic User-Agent (no personal name or email)

Data-integrity habits:
  * every successful JSON response is saved, unchanged, under raw/<run_id>/
  * every failed call is written to logs/failed_calls_<run_id>.csv with the reason
  * the client never fills in or guesses a value; a failed call returns None

Authentication: the API worked with no token when this project was built.
The spec also lists an OAuth2 client-credentials scheme. If the API ever answers
401/403, this client stops and prints how to get credentials (see AuthRequired).
"""

import csv
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE_URL = "https://api.fortnite.com/ecosystem/v1"
USER_AGENT = "fortnite-ecosystem-class-project/1.0 (python-requests)"
DELAY_SECONDS = 0.6      # pause before every request
MAX_RETRIES = 4          # extra attempts after a 429 / 5xx / network error
MAX_REQUESTS = 400       # hard cap on HTTP requests in one run (retries count too)
TIMEOUT_SECONDS = 30

AUTH_HELP = """
The Fortnite Data API answered 401/403 (authentication required).
When this project was built the API needed no token, so this is a change on Epic's side.
To get credentials:
  1. Sign in at https://dev.epicgames.com/portal and create (or open) a product.
  2. Under Product Settings > Clients, create a client and note its Client ID and Client Secret.
  3. Put them in a file named .env in this folder (never commit it; it is in .gitignore):
        FORTNITE_CLIENT_ID=...
        FORTNITE_CLIENT_SECRET=...
  4. The spec's token URL is https://api.epicgames.dev/epic/oauth/v1/token (client-credentials flow).
Then ask for the client to be extended to request a token. Nothing was guessed or filled in.
"""


class AuthRequired(Exception):
    """Raised when the API answers 401 or 403."""


class FortniteClient:
    def __init__(self, run_id, raw_dir="raw", log_dir="logs", max_requests=MAX_REQUESTS):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.raw_dir = Path(raw_dir) / run_id
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        Path(log_dir).mkdir(exist_ok=True)
        self.fail_log_path = Path(log_dir) / f"failed_calls_{run_id}.csv"
        self.max_requests = max_requests
        self.http_requests = 0   # every HTTP request sent, including retries
        self.calls = 0           # logical calls (one per get())
        self.failures = []       # one dict per logical call that finally failed
        # Write the log header now so an empty log still proves nothing failed.
        with open(self.fail_log_path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["time_utc", "path", "params", "status", "reason"])

    # ------------------------------------------------------------------ helpers
    def _log_failure(self, path, params, status, reason):
        row = {
            "time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "path": path,
            "params": json.dumps(params or {}),
            "status": status,
            "reason": reason,
        }
        self.failures.append(row)
        with open(self.fail_log_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row.values())

    def _raw_filename(self, path, params):
        # e.g. /islands/1234-5678-9012/metrics/day -> islands_1234-5678-9012_metrics_day.json
        name = path.strip("/").replace("/", "_")
        if params:
            extra = "_".join(f"{k}-{v}" for k, v in sorted(params.items()) if k not in ("from", "to"))
            if extra:
                name += "__" + extra
        name = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
        return self.raw_dir / f"{name}.json"

    # --------------------------------------------------------------------- main
    def get(self, path, params=None):
        """GET BASE_URL + path. Returns parsed JSON, or None if the call failed."""
        self.calls += 1
        url = BASE_URL + path
        last_reason, last_status = "unknown", ""

        for attempt in range(MAX_RETRIES + 1):
            if self.http_requests >= self.max_requests:
                self._log_failure(path, params, "", f"request cap of {self.max_requests} reached")
                return None
            time.sleep(DELAY_SECONDS)
            self.http_requests += 1
            try:
                resp = self.session.get(url, params=params, timeout=TIMEOUT_SECONDS)
            except requests.RequestException as exc:
                last_status, last_reason = "", f"network error: {exc.__class__.__name__}"
                time.sleep(2 ** attempt)
                continue

            if resp.status_code == 200:
                data = resp.json()
                with open(self._raw_filename(path, params), "w", encoding="utf-8") as f:
                    json.dump({"url": resp.url, "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                               "response": data}, f, ensure_ascii=False, indent=1)
                return data

            if resp.status_code in (401, 403):
                self._log_failure(path, params, resp.status_code, "authentication required")
                raise AuthRequired(AUTH_HELP)

            last_status = resp.status_code
            last_reason = resp.text[:200].replace("\n", " ")
            if resp.status_code == 429 or resp.status_code >= 500:
                # Back off: use Retry-After if given, else 2, 4, 8, 16 seconds.
                retry_after = resp.headers.get("Retry-After", "")
                wait = int(retry_after) if retry_after.isdigit() else 2 ** (attempt + 1)
                time.sleep(wait)
                continue
            break  # 400 / 404 etc. will not improve with a retry

        self._log_failure(path, params, last_status, last_reason)
        return None

    def failure_rate(self):
        return len(self.failures) / self.calls if self.calls else 0.0
