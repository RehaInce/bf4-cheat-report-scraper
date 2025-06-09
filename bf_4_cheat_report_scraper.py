#!/usr/bin/env python3
import requests
import re
import csv
import sys
from urllib.parse import urljoin
from datetime import datetime, timezone


def format_datetime(timestamp):
    """
    Convert a UNIX timestamp (seconds since epoch) to a UTC string in the format:
        YYMMDD HH:MM
    """
    return datetime.fromtimestamp(int(timestamp), timezone.utc).strftime("%y%m%d %H:%M")


def main():
    # --- Prompt user for input URL ---
    url = input("Please enter the bf4cheatreport.com URL: ").strip()

    # --- Fetch page HTML ---
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code} fetching page", file=sys.stderr)
        sys.exit(1)
    html = response.text

    # --- Extract JSON endpoint path from cr_url variable ---
    match = re.search(r'var\s+cr_url\s*=\s*"([^"]+)"\s*;', html)
    if not match:
        print("Error: could not find cr_url in page source", file=sys.stderr)
        sys.exit(1)
    cr_path = match.group(1)

    # --- Fetch JSON data from the derived endpoint ---
    json_url = urljoin(url, cr_path)
    json_resp = requests.get(json_url)
    if json_resp.status_code != 200:
        print(f"Error: HTTP {json_resp.status_code} fetching JSON", file=sys.stderr)
        sys.exit(1)
    data = json_resp.json()

    reports = data.get("br_array", [])
    if not reports:
        print("No reports found in JSON response", file=sys.stderr)
        sys.exit(1)

    # --- Determine output filename from the first personaName ---
    persona = reports[0].get("personaName", "output")
    safe_name = re.sub(r'[^0-9A-Za-z_-]', '_', persona)
    filename = f"{safe_name}.csv"

    # --- Define CSV headers in the exact order as the site UI ---
    headers = [
        "dateTime", "ssss", "min",
        "reportId", "pid", "personaName", "rank", "age", "vd", "bestVehicle", "bvk",
        "k", "d", "hs", "spot", "fird", "hit", "bwk", "bestWeap", "spm",
        "kpm", "kdr", "hskr", "bwhs", "acc", "kph", "max1", "max2",
    ]

    # --- Write data to CSV (overwriting if file exists) ---
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for r in reports:
            row = [
                format_datetime(r.get("createdAt", 0)),         # dateTime
                r.get("duration", ""),                       # ssss
                r.get("playMinutes", ""),                    # min

                r.get("reportId", ""),                       # reportId
                r.get("personaId", ""),                      # pid
                r.get("personaName", ""),                    # personaName
                r.get("rank", ""),                           # rank
                r.get("userAgeDays", ""),                    # age
                r.get("vehDestroyed", ""),                   # vd
                r.get("vehBest", ""),                        # bestVehicle
                r.get("vehBestKills", ""),                   # bvk

                r.get("kills", ""),                          # k
                r.get("deaths", ""),                         # d
                r.get("headShots", ""),                      # hs
                r.get("R7", 0) * 4,                            # spot (4 × R7)
                r.get("shotsFired", ""),                     # fird
                r.get("shotsHit", ""),                       # hit
                r.get("bwKills", ""),                        # bwk
                r.get("bestWeapon", ""),                     # bestWeap
                r.get("spm", ""),                            # spm

                r.get("kpm", ""),                            # kpm
                r.get("kdr", ""),                            # kdr
                r.get("hskrPct", ""),                        # hskr
                r.get("bwHskrPct", ""),                      # bwhs
                r.get("accuracy", ""),                       # acc
                r.get("killsPerHitPct", ""),                 # kph
                r.get("kphMax1", ""),                        # max1
                r.get("kphMax2", ""),                        # max2
            ]
            writer.writerow(row)

    print(f"✅ Done! CSV saved as {filename}")


if __name__ == "__main__":
    main()
