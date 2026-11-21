#!/usr/bin/env python3
"""Fetch the last year of contributions and the merged PR count into data/profile.json.

Token: $GH_TOKEN or $GITHUB_TOKEN, falling back to `gh auth token` locally. It needs
read:user for private contributions to be counted, as they are on the profile page.
"""
import datetime
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "data", "profile.json")
USER = "lupsalexandra33"
QUERY = """query($login:String!){ user(login:$login){
  pullRequests(states:MERGED){ totalCount }
  contributionsCollection{ contributionCalendar{ totalContributions
    weeks{ contributionDays{ date contributionCount } } } } } }"""


def token():
    found = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if found:
        return found
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        sys.exit("no token: set GH_TOKEN")


def main():
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token()}", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.load(response)
    if "errors" in body:
        sys.exit(f"graphql error: {body['errors']}")

    user = body["data"]["user"]
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = [
        {"date": day["date"], "count": day["contributionCount"]}
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]
    out = {
        "user": USER,
        "fetched": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "total": calendar["totalContributions"],
        "merged_prs": user["pullRequests"]["totalCount"],
        "days": days,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote data/profile.json: {out['total']} contributions, {out['merged_prs']} merged PRs")


if __name__ == "__main__":
    main()
