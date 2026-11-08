import pytest

from llmx_netlab.backbone import STAGES, BigramSLM
from llmx_netlab.domain import code_interpreter, convert_bandwidth, transfer_time
from llmx_netlab.gateway import Vocabulary, describe_media
from llmx_netlab.kb import all_entries, corpus_text
from llmx_netlab.memory import SessionMemory
from llmx_netlab.mlops import run_benchmark
from llmx_netlab.rag import RagSystem


def test_kb_size():
    assert len(all_entries()) >= 20


def test_code_interpreter_safe_math():
    assert code_interpreter("2 + 3 * 4") == 14
    with pytest.raises(Exception):
        code_interpreter("__import__('os').system('id')")


def test_bandwidth_math():
    assert convert_bandwidth(1, "Gbps", "Mbps") == 1000
    assert transfer_time(100, 100) == 8.0


def test_tokenizer_vocab():
    v = Vocabulary(corpus_text())
    assert len(v) > 100
    assert v.encode("router switch") != []


def test_media_contract_never_decodes():
    out = describe_media("image", b"\x89PNG....")
    assert out["decoded"] is False


def test_slm_generates_from_kb_words():
    slm = BigramSLM()
    out = slm.generate("a router connects")
    assert "router" in out


def test_stages_contract():
    names = [s["stage"] for s in STAGES]
    assert any("pre-training" in n for n in names)
    assert any("RLHF" in n for n in names)


def test_session_memory_window():
    m = SessionMemory(max_turns=2)
    m.add("user", "a"); m.add("assistant", "b"); m.add("user", "c")
    assert len(m.turns) == 2


def test_benchmark_accuracy():
    out = run_benchmark(RagSystem())
    assert out["accuracy"] >= 0.8
