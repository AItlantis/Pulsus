from agents.pulsus.config.settings import load_settings, Settings

def test_load_settings_default_paths(tmp_path):
    s = load_settings()
    assert isinstance(s, Settings)
    assert s.workflows_root.exists()
    assert s.log_dir.exists()
    assert 0 < s.sandbox.max_seconds <= 60

def test_model_provider_is_ollama():
    s = load_settings()
    assert s.model.provider == "ollama"
