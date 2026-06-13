"""THROWAWAY — verifies the CI gate blocks a failing-test PR. Delete this branch."""
import unittest


class TestGateProof(unittest.TestCase):
    def test_intentional_failure_proving_the_gate_blocks(self):
        self.fail("Intentional failure: proving the required CI check blocks merge. "
                  "This branch (test/gate-proof-deleteme) is to be deleted.")


if __name__ == "__main__":
    unittest.main()
