"""
Very lightweight functional checks.
Run:  python tests.py
"""
from agent import run_agent

def test_basic():
    out = run_agent("pilot for cats", lambda x: None)
    assert "score" in out.lower() or any(c.isdigit() for c in out), "No score produced"

def test_edge():
    out = run_agent("quantum scientist on jupiter", lambda x: None)
    # Should still return some answer, not crash
    assert len(out) > 10

if __name__ == "__main__":
    test_basic()
    test_edge()
    print("✅ All tests passed.")
