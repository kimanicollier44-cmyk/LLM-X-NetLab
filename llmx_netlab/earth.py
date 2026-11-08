"""Google Earth seat — KML export for a tracked path.

The lab builds a KML document (the file format Google Earth opens)
from a tracked path: a Placemark for the START, each MIDDLE point and
the END, plus a LineString for the path. Coordinates are supplied by
the caller for their own points; when none are supplied the export
carries NO coordinates and says so — this lab never geolocates an IP
(geolocate_real_ip is a HOLD action) and never calls Google Earth.
"""
from xml.sax.saxutils import escape


def build_kml(track, coords=None, name="LLM-X-NetLab path"):
    """coords: optional {ip: (lat, lon)} for the caller's own points."""
    coords = coords or {}
    missing = [h["ip"] for h in track["path"] if h["ip"] not in coords]
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<kml xmlns="http://www.opengis.net/kml/2.2">', "<Document>",
             f"<name>{escape(name)}</name>"]
    if missing:
        parts.append(f"<!-- no coordinates supplied for: {', '.join(missing)} — "
                     "placemarks omitted for those hops; this lab does not geolocate IPs -->")
    line = []
    for h in track["path"]:
        if h["ip"] not in coords:
            continue
        lat, lon = coords[h["ip"]]
        line.append(f"{lon},{lat},0")
        label = "START" if h["hop"] == 1 else ("END" if h["hop"] == track["total_hops"] else f"Hop {h['hop']} (middle)")
        parts.append("<Placemark>"
                     f"<name>{label}: {escape(h['ip'])}</name>"
                     f"<description>{escape(h['role'])} — class {h['class']}, {escape(h['scope'])}</description>"
                     f"<Point><coordinates>{lon},{lat},0</coordinates></Point>"
                     "</Placemark>")
    if len(line) >= 2:
        parts.append("<Placemark><name>Path</name><LineString>"
                     f"<coordinates>{' '.join(line)}</coordinates>"
                     "</LineString></Placemark>")
    parts.append("</Document></kml>")
    return "\n".join(parts)


SEAT = {"name": "Google Earth", "mode": "KML file export only",
        "live_call": False,
        "note": "open the exported .kml in Google Earth yourself; nothing is uploaded by this lab"}
