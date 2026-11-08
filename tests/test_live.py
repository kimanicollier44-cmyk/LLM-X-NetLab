import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pytest

from llmx_netlab import live


@pytest.fixture()
def tcp_server():
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(4)
    port = srv.getsockname()[1]
    yield port
    srv.close()


def test_tcp_connect_open_and_closed(tcp_server):
    assert live.tcp_connect("127.0.0.1", tcp_server)["open"] is True
    assert live.tcp_connect("127.0.0.1", 9)["open"] is False  # discard port, closed here


def test_port_scan_finds_listener(tcp_server):
    out = live.port_scan("127.0.0.1", ports=[tcp_server, 9])
    assert out["open_count"] == 1
    assert out["open"][0]["port"] == tcp_server


def test_dns_localhost():
    out = live.dns_lookup("localhost")
    assert "127.0.0.1" in out["addresses"]


def test_ping_loopback_reachable(tcp_server):
    # ping_host labels its method honestly: "icmp (system ping)" where the
    # machine permits ping (e.g. GitHub-hosted runners), "tcp timing ..."
    # where ICMP is blocked (e.g. a sandbox with no CAP_NET_RAW). Either
    # way a loopback host with a live listener must read as reachable.
    out = live.ping_host("127.0.0.1", fallback_ports=(tcp_server,))
    if out["method"].startswith("icmp"):
        assert out["replies"] >= 1
    else:
        assert out["method"].startswith("tcp timing")
        assert out["reachable"] is True


def test_http_probe_local():
    httpd = HTTPServer(("127.0.0.1", 0), SimpleHTTPRequestHandler)
    port = httpd.server_address[1]
    th = threading.Thread(target=httpd.serve_forever, daemon=True)
    th.start()
    try:
        out = live.http_probe(f"http://127.0.0.1:{port}/")
        assert out["status"] == 200
    finally:
        httpd.shutdown()


def test_geo_shape():
    out = live.geo_lookup("1.1.1.1")
    assert out["ip"] == "1.1.1.1" and "found" in out
