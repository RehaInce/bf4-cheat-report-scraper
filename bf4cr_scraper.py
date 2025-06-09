#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape bf4cheatreport.com player data into CSV"
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="bf4cheatreport.com URL to scrape (will prompt if omitted)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output CSV file name. Defaults to <persona>.csv",
    )
    return parser.parse_args()


def format_datetime(timestamp):
    """
    Convert a UNIX timestamp (seconds since epoch) to a UTC string in the format:
        YYMMDD HH:MM
    """
    return datetime.fromtimestamp(int(timestamp), timezone.utc).strftime("%y%m%d %H:%M")


def main() -> None:
    args = parse_args()

    # --- Prompt user for input URL if not provided ---
    url = args.url
    if not url:
        url = input("Please enter the bf4cheatreport.com URL: ").strip()

    # --- Fetch page HTML ---
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Error fetching page: {exc}", file=sys.stderr)
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
    try:
        json_resp = requests.get(json_url, timeout=10)
        json_resp.raise_for_status()
        data = json_resp.json()
    except requests.RequestException as exc:
        print(f"Error fetching JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    reports = data.get("br_array", [])
    if not reports:
        print("No reports found in JSON response", file=sys.stderr)
        sys.exit(1)

    # --- Determine output filename ---
    persona = reports[0].get("personaName", "output")
    safe_name = re.sub(r"[^0-9A-Za-z_-]", "_", persona)
    filename = args.output if args.output else f"{safe_name}.csv"

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
