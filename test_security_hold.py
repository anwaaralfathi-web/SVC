import ast
import unittest
from pathlib import Path

APP = Path(__file__).with_name("svc_assess_ppeng01_emergency_security_hold.py")

class SecurityHoldTests(unittest.TestCase):
    def test_python_syntax_is_valid(self):
        ast.parse(APP.read_text(encoding="utf-8"))

    def test_guard_stops_before_database_initialization(self):
        source = APP.read_text(encoding="utf-8")
        stop_pos = source.index("st.stop()")
        actual_init = source.index("\ninit_db()", source.index("def init_db():"))
        self.assertLess(stop_pos, actual_init)

    def test_hold_is_fail_closed_and_explicit(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("SECURITY HOLD", source)
        self.assertIn("temporarily unavailable", source)
        self.assertNotIn('if os.getenv("SVC_SECURITY_HOLD")', source)

if __name__ == "__main__":
    unittest.main(verbosity=2)
