"""
    Tests that the interop aspects classes sit on the suite-wide aspects hierarchy rooted at
    :class:`ccai.aspects.aspects.Aspects`, and keep their identity, hashing and freezing semantics.
"""

import ccai.testbase as testbase

from ccai.aspects.aspects import Aspects as AspectsBase
from ccai.bases.freezable import Freezable
from ccai.interop.aspects import Aspects, AspectsCmd, DEFAULT_ASPECTS, DEFAULT_CMD_ASPECTS


def test_interop_aspects_derive_from_the_foundations_base():
    testbase.assert_true(issubclass(Aspects, AspectsBase))
    testbase.assert_true(issubclass(AspectsCmd, Aspects))
    testbase.assert_true(isinstance(DEFAULT_CMD_ASPECTS, AspectsBase))


def test_interop_aspects_are_freezable_and_frozen_by_default():
    testbase.assert_true(isinstance(DEFAULT_ASPECTS, Freezable))
    try:
        DEFAULT_ASPECTS.completion_timeout = 1
        testbase.assert_true(False, "assignment to a frozen aspects object must raise")
    except AttributeError:
        # Expected: a frozen aspects object rejects attribute assignment, which is what this test verifies.
        pass


def test_interop_aspects_compare_by_identity_and_hash():
    first = Aspects()
    second = Aspects()
    testbase.assert_true(first != second)
    testbase.assert_equal(len({first, second}), 2)


def test_base_fields_flow_through_the_interop_constructor():
    aspects = AspectsCmd(expected_status=(0, 1), completion_timeout=42, max_attempts=3, logger_name="ccai.test")
    testbase.assert_equal(aspects.completion_timeout, 42)
    testbase.assert_equal(aspects.max_attempts, 3)
    testbase.assert_equal(aspects.logger_name, "ccai.test")
    testbase.assert_equal(aspects.expected_status, (0, 1))
