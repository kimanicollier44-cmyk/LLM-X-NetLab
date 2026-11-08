from llmx_netlab import iphop
from llmx_netlab.brains.carbon4 import HOLD_ACTIONS
from llmx_netlab.earth import build_kml
from llmx_netlab.flowvideo import plan_video


def test_track_start_middle_end():
    trk = iphop.track_path(["192.168.1.1", "10.0.0.1", "203.0.113.10"])
    assert trk["start"]["ip"] == "192.168.1.1"
    assert trk["middle_count"] == 1
    assert trk["middle"][0]["ip"] == "10.0.0.1"
    assert trk["end"]["ip"] == "203.0.113.10"
    assert trk["start"]["is_private"] is True
    assert trk["end"]["is_private"] is False


def test_track_topology_simulated():
    trk = iphop.track_topology("star", 6, 1, 4)
    assert trk["simulated"] is True
    assert trk["start"]["ip"] == "192.168.1.1"
    assert trk["end"]["ip"] == "203.0.113.10"


def test_map_render():
    trk = iphop.track_path(["10.0.0.1", "10.0.0.2"])
    text = iphop.render_map(trk)
    assert "START" in text and "END" in text


def test_earth_kml_no_fake_geolocation():
    trk = iphop.track_path(["192.168.1.1", "203.0.113.10"])
    kml = build_kml(trk)  # no coords supplied
    assert "does not geolocate" in kml
    assert "<Placemark><name>START" not in kml  # no invented positions


def test_earth_kml_with_own_coords():
    trk = iphop.track_path(["192.168.1.1", "203.0.113.10"])
    kml = build_kml(trk, {"192.168.1.1": (34.05, -118.24), "203.0.113.10": (40.71, -74.0)})
    assert "START: 192.168.1.1" in kml and "END: 203.0.113.10" in kml


def test_flow_plan_is_plan_only():
    plan = plan_video("OSI model")
    assert plan["render"].startswith("HOLD")
    assert plan["total_seconds"] > 0


def test_tracking_real_people_is_held():
    assert "geolocate_real_ip" in HOLD_ACTIONS
    assert "track_person_device" in HOLD_ACTIONS
