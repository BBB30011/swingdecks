import pytest
from pathlib import Path
from core.queue import FileQueue

def test_queue_dir_creation(tmp_path):
    # Test 1: Queue directory otomatis dibuat jika belum ada.
    q_dir = tmp_path / "queue_01"
    q = FileQueue(q_dir)
    assert q_dir.exists()
    assert q.completed_dir.exists()
    assert q.failed_dir.exists()

def test_enqueue_creates_json(tmp_path):
    # Test 2: enqueue() membuat JSON.
    q = FileQueue(tmp_path / "queue_01")
    q.enqueue("JOB-001", {"symbol": "BBCA"})
    assert (tmp_path / "queue_01" / "JOB-001.json").exists()

def test_dequeue_reads_json(tmp_path):
    # Test 3: Isi JSON dapat dibaca kembali.
    q = FileQueue(tmp_path / "queue_01")
    q.enqueue("JOB-002", {"symbol": "BBRI"})
    data = q.dequeue()
    assert data is not None
    assert data["job_id"] == "JOB-002"
    assert data["payload"]["symbol"] == "BBRI"

def test_dequeue_ignores_tmp(tmp_path):
    # Test 4: .tmp tidak dibaca oleh dequeue().
    q_dir = tmp_path / "queue_01"
    q = FileQueue(q_dir)
    (q_dir / "JOB-003.json.tmp").write_text('{"job_id": "J3"}', encoding="utf-8")
    assert q.dequeue() is None

def test_duplicate_job_rejected(tmp_path):
    # Test 5: Duplicate job_id ditolak.
    q = FileQueue(tmp_path / "queue_01")
    q.enqueue("JOB-004", {"symbol": "ASII"})
    with pytest.raises(FileExistsError):
        q.enqueue("JOB-004", {"symbol": "TLKM"})

def test_empty_queue_returns_none(tmp_path):
    # Test 6: Queue kosong menghasilkan None.
    q = FileQueue(tmp_path / "queue_01")
    assert q.dequeue() is None

def test_complete_moves_file(tmp_path):
    # Test 7: complete() memindahkan file ke queue/completed/
    q = FileQueue(tmp_path / "queue_01")
    q.enqueue("JOB-005", {"symbol": "GOTO"})
    q.dequeue()
    q.complete("JOB-005")
    assert not (tmp_path / "queue_01" / "JOB-005.json").exists()
    assert (tmp_path / "completed" / "JOB-005.json").exists()

def test_fail_moves_file(tmp_path):
    # Test 8: fail() memindahkan file ke queue/failed/
    q = FileQueue(tmp_path / "queue_01")
    q.enqueue("JOB-006", {"symbol": "BMRI"})
    q.dequeue()
    q.fail("JOB-006")
    assert not (tmp_path / "queue_01" / "JOB-006.json").exists()
    assert (tmp_path / "failed" / "JOB-006.json").exists()

def test_corrupt_json_raises_error(tmp_path):
    # Test 9: JSON corrupt menghasilkan error yang jelas.
    q_dir = tmp_path / "queue_01"
    q = FileQueue(q_dir)
    (q_dir / "JOB-007.json").write_text('{bad json"', encoding="utf-8")
    with pytest.raises(ValueError, match="corrupt"):
        q.dequeue()

def test_atomic_write_no_tmp_left(tmp_path):
    # Test 10: Atomic write tidak meninggalkan file temporary.
    q_dir = tmp_path / "queue_01"
    q = FileQueue(q_dir)
    q.enqueue("JOB-008", {"symbol": "BBNI"})
    tmp_files = list(q_dir.glob("*.tmp"))
    assert len(tmp_files) == 0
