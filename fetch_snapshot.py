#!/usr/bin/env python3
"""
Fetch the latest orbital snapshot from Space-Track, split into curated layers,
and write compressed files the app can download from a CDN.

Runs at most ONCE PER HOUR (Space-Track rule). Credentials come from env vars
SPACETRACK_USER / SPACETRACK_PASS (set as GitHub Actions secrets).
"""
import os, sys, json, gzip, time, pathlib, urllib.parse
import requests

USER = os.environ["SPACETRACK_USER"]
PASS = os.environ["SPACETRACK_PASS"]

BASE = "https://www.space-track.org"
LOGIN = f"{BASE}/ajaxauth/login"
# Bandwidth-optimized query from Space-Track docs: on-orbit, propagable elsets, JSON.
QUERY = (f"{BASE}/basicspacedata/query/class/gp/"
         "decay_date/null-val/epoch/%3Enow-10/"
         "orderby/NORAD_CAT_ID/format/json")

OUT = pathlib.Path("public")           # committed + served via CDN
OUT.mkdir(exist_ok=True)

def fetch():
    s = requests.Session()
    r = s.post(LOGIN, data={"identity": USER, "password": PASS}, timeout=60)
    r.raise_for_status()
    r = s.get(QUERY, timeout=180)
    r.raise_for_status()
    s.get(f"{BASE}/ajaxauth/logout", timeout=30)
    return r.json()

def slim(o):
    """Keep only the fields the app needs to propagate + label an object."""
    return {
        "id":   o["NORAD_CAT_ID"],
        "name": o["OBJECT_NAME"],
        "type": o["OBJECT_TYPE"],      # PAYLOAD / ROCKET BODY / DEBRIS / UNKNOWN
        "l1":   o["TLE_LINE1"],
        "l2":   o["TLE_LINE2"],
    }

def write(name, rows):
    data = json.dumps({"epoch": int(time.time()), "count": len(rows), "objects": rows},
                      separators=(",", ":")).encode()
    (OUT / f"{name}.json").write_bytes(data)                    # plain
    with gzip.open(OUT / f"{name}.json.gz", "wb") as f:         # ~5-10x smaller
        f.write(data)
    gz_kb = (OUT / f"{name}.json.gz").stat().st_size // 1024
    print(f"  {name:<12} {len(rows):>6} objects  {len(data)//1024:>5} KB  ({gz_kb} KB gz)")

def main():
    print("Fetching Space-Track snapshot...")
    raw = fetch()
    objs = [slim(o) for o in raw if o.get("TLE_LINE1") and o.get("TLE_LINE2")]
    print(f"Total on-orbit objects: {len(objs)}")

    # ---- Curated layers the app can load independently ----
    starlink = [o for o in objs if o["name"].upper().startswith("STARLINK")]
    debris   = [o for o in objs if o["type"] == "DEBRIS"]
    payloads = [o for o in objs if o["type"] == "PAYLOAD"]
    # "Featured": stations + famous science craft the app highlights by default.
    FEATURED_IDS = {"25544", "48274", "20580", "43013", "40379"}  # ISS, Tiangong, Hubble, NOAA-20, ...
    featured = [o for o in objs if o["id"] in FEATURED_IDS]

    print("Writing layers -> public/")
    write("all",      objs)       # full catalog (heavy; optional for app)
    write("payloads", payloads)   # active-ish satellites
    write("starlink", starlink)
    write("debris",   debris)
    write("featured", featured)   # tiny, load-on-launch default set
    print("Done.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
