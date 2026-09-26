import pytest
from core.state_machine import transition

def test_valid_transitions():
    assert transition("CREATED", "PROCESSING") is True
    assert transition("PROCESSING", "COMPLETED") is True
    assert transition("PROCESSING", "RETRY") is True
    assert transition("PROCESSING", "FAILED") is True
    assert transition("RETRY", "PROCESSING") is True
    assert transition("RETRY", "FAILED") is True
    assert transition("FAILED", "DEAD_LETTER") is True

def test_invalid_transition_completed_to_processing():
    with pytest.raises(ValueError):
        transition("COMPLETED", "PROCESSING")

def test_invalid_transition_dead_letter_to_processing():
    with pytest.raises(ValueError):
        transition("DEAD_LETTER", "PROCESSING")

def test_invalid_transition_created_to_completed():
    with pytest.raises(ValueError):
        transition("CREATED", "COMPLETED")

def test_invalid_transition_created_to_failed():
    with pytest.raises(ValueError):
        transition("CREATED", "FAILED")
