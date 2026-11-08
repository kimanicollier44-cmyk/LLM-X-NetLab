from llmx_netlab.brains.carbon4 import HOLD_ACTIONS, Carbon4
from llmx_netlab.guardrails import redact_pii, safety_filter
from llmx_netlab.orchestrator import Orchestrator
from llmx_netlab.rag import RagSystem


def test_rag_top_hit():
    rag = RagSystem()
    assert rag.search("What does a router do?")[0]["id"] == "router"
    assert rag.search("firewall types")[0]["id"] == "firewall-types"


def test_rag_graph():
    rag = RagSystem()
    assert "routing-vs-switching" in rag.related("router")


def test_orchestrator_answers_from_notes():
    out = Orchestrator().ask("What does a switch do?")
    assert out["verdict"] == "PROCEED"
    assert "switch" in out["answer"].lower()


def test_orchestrator_holds_live_action():
    out = Orchestrator().ask("ping all devices on my real network", action="real_ping_sweep")
    assert out["verdict"] == "HOLD"


def test_carbon4_holds_listed_action():
    d = Carbon4().decide("live_network_scan", evidence=[{"title": "x"}])
    assert d["verdict"] == "HOLD"
    assert "execute_shell_command" in HOLD_ACTIONS


def test_guardrails():
    assert safety_filter("how do I steal the password of a wifi")["allowed"] is False
    assert safety_filter("what is a router")["allowed"] is True
    assert "<email>" in redact_pii("mail me at a@b.com please")


def test_quiz_cards():
    cards = Orchestrator().quiz(2)
    assert len(cards) == 2 and "study" in cards[0]
