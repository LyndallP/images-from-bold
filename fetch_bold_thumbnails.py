#!/usr/bin/env python3
"""
fetch_bold_thumbnails.py

Fetch image thumbnails from the BOLD (Barcode of Life Data Systems) CAOS API
for one or more process IDs and output markdown image syntax.

No API key required. Uses the public CAOS endpoints:
  https://caos.boldsystems.org/api/images?processids=<ids>
  https://caos.boldsystems.org/api/objects/<objectid>

Usage:
  python fetch_bold_thumbnails.py BAYS528-24
  python fetch_bold_thumbnails.py BAYS528-24 BBF341-13 ABINP144-21
  python fetch_bold_thumbnails.py --file processids.txt
  python fetch_bold_thumbnails.py BAYS528-24 > thumbnails.md
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from urllib.parse import urlencode

BASE_URL = "https://caos.boldsystems.org/api/images?processids="
IMAGE_URL = "https://caos.boldsystems.org/api/objects/"
BATCH_SIZE = 100        # max process IDs per request
URL_MAX_LEN = 7500      # safe URL length limit (mirrors the Perl scripts)
SLEEP_BETWEEN = 0.5    # seconds to wait between batches


def fetch_image_map(processids):
    """
    Query the CAOS API for a list of process IDs.
    Returns a dict mapping processid -> objectid for those that have images.
    """
    # Split into sub-batches that stay under the URL length limit
    sub_batches = []
    current = []
    current_len = 0
    for pid in processids:
        if current_len + len(pid) + 1 > URL_MAX_LEN and current:
            sub_batches.append(current)
            current = [pid]
            current_len = len(pid)
        else:
            current.append(pid)
            current_len += len(pid) + 1
    if current:
        sub_batches.append(current)

    image_map = {}
    for batch in sub_batches:
        url = BASE_URL + ",".join(batch)
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "images-from-bold/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for entry in data:
                pid = entry.get("processid")
                oid = entry.get("objectid")
                if pid and oid:
                    image_map[pid] = oid
        except urllib.error.HTTPError as e:
            print(f"<!-- HTTP error {e.code} fetching batch: {e.reason} -->", file=sys.stderr)
        except urllib.error.URLError as e:
            print(f"<!-- URL error fetching batch: {e.reason} -->", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"<!-- Failed to parse JSON response: {e} -->", file=sys.stderr)
        time.sleep(SLEEP_BETWEEN)

    return image_map


def render_markdown(processids, image_map):
    """Print one markdown line per process ID."""
    for pid in processids:
        if pid in image_map:
            oid = image_map[pid]
            print(f"![{pid}]({IMAGE_URL}{oid})")
        else:
            print(f"<!-- {pid}: no image found -->")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch BOLD image thumbnails and output markdown."
    )
    parser.add_argument(
        "processids",
        nargs="*",
        metavar="PROCESSID",
        help="One or more BOLD process IDs (e.g. BAYS528-24)",
    )
    parser.add_argument(
        "--file", "-f",
        metavar="FILE",
        help="Text file with one process ID per line",
    )
    args = parser.parse_args()

    processids = list(args.processids)

    if args.file:
        try:
            with open(args.file) as fh:
                for line in fh:
                    pid = line.strip()
                    if pid and not pid.startswith("#"):
                        processids.append(pid)
        except OSError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)

    if not processids:
        parser.print_help()
        sys.exit(1)

    # Deduplicate while preserving order
    seen = set()
    unique_ids = []
    for pid in processids:
        if pid not in seen:
            seen.add(pid)
            unique_ids.append(pid)

    # Process in batches
    image_map = {}
    for i in range(0, len(unique_ids), BATCH_SIZE):
        batch = unique_ids[i:i + BATCH_SIZE]
        image_map.update(fetch_image_map(batch))

    render_markdown(unique_ids, image_map)


if __name__ == "__main__":
    main()
