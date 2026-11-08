from llmx_netlab import netlab


def test_subnet_basic():
    info = netlab.subnet_info("192.168.1.0/24")
    assert info["network"] == "192.168.1.0"
    assert info["broadcast"] == "192.168.1.255"
    assert info["usable_hosts"] == 254
    assert info["is_private"] is True
    assert info["class"]["class"] == "C"


def test_subnet_slash16():
    info = netlab.subnet_info("10.0.0.0/16")
    assert info["usable_hosts"] == 65534
    assert info["class"]["class"] == "A"


def test_topology_star_spof():
    out = netlab.analyse_topology("star", 6)
    assert out["links"] == 5
    assert out["single_points_of_failure"] == [0]


def test_topology_mesh_resilient():
    out = netlab.analyse_topology("mesh", 5)
    assert out["links"] == 10
    assert out["single_points_of_failure"] == []


def test_topology_bus_chain():
    out = netlab.analyse_topology("bus", 5)
    assert out["links"] == 4
    assert out["worst_case_hops"] == 4


def test_layers():
    assert netlab.layer_of("router")["osi_layer"] == 3
    assert netlab.layer_of("switch")["osi_layer"] == 2
    assert netlab.layer_of("http")["tcpip_layer"] == 4


def test_ping_simulated_only():
    out = netlab.simulate_ping("ring", 6, 0, 3)
    assert out["simulated"] is True
    assert out["reachable"] is True
    assert out["hops"] == 3


def test_device_advisor():
    assert netlab.advise_device("connect two different networks")["device"] == "router"
    assert netlab.advise_device("I need wifi in the office")["device"] == "access point"
