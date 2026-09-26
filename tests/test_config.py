from core.config import load_yaml
import pytest

def test_load_settings_yaml():
    data = load_yaml('settings.yaml')
    assert isinstance(data, dict)
    assert 'project' in data

def test_load_models_yaml():
    data = load_yaml('models.yaml')
    assert isinstance(data, dict)
    assert 'models' in data

def test_load_risk_yaml():
    data = load_yaml('risk.yaml')
    assert isinstance(data, dict)
    assert 'risk' in data

def test_load_universe_yaml():
    data = load_yaml('universe.yaml')
    assert isinstance(data, dict)
    assert 'universe' in data
