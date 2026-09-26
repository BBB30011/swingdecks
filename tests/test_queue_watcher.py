from pathlib import Path
from core.queue_watcher import QueueWatcher
import shutil
import pytest

@pytest.fixture(autouse=True)
def clean_queue():
    path = Path("test_watch_queue")
    if path.exists():
        shutil.rmtree(path)
    yield
    if path.exists():
        shutil.rmtree(path)

def test_queue_watcher_ignores_tmp():
    watcher = QueueWatcher("test_watch_queue")
    with open("test_watch_queue/test.tmp", "w") as f:
        f.write("tmp")
    with open("test_watch_queue/test.json", "w") as f:
        f.write("json")
        
    files = watcher.poll()
    assert len(files) == 1
    assert files[0].name == "test.json"
