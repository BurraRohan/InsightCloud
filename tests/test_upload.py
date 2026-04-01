"""
test_upload.py — Tests for InsightCloud upload module.
Tests CSV validation, file saving, and file listing.
"""

import pytest
import os
import sys
import io
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set to local mode for testing BEFORE importing config
os.environ["STORAGE_MODE"] = "local"
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp()

import config
# Force-patch config values in case .env overrode them
config.STORAGE_MODE = "local"
config.UPLOAD_DIR = os.environ["UPLOAD_DIR"]

from upload import validate_csv, save_file, list_files, load_file_as_df, ensure_upload_dir
import upload
upload.UPLOAD_DIR = os.environ["UPLOAD_DIR"]

from config import UPLOAD_DIR


# ─── Helper: Create fake uploaded file ─────────────────────

class FakeUploadedFile:
    """Mock Streamlit UploadedFile for testing."""

    def __init__(self, name: str, content: bytes):
        self.name = name
        self.size = len(content)
        self._content = content
        self._stream = io.BytesIO(content)

    def read(self, *args, **kwargs):
        return self._stream.read(*args, **kwargs)

    def readline(self, *args, **kwargs):
        return self._stream.readline(*args, **kwargs)

    def readlines(self, *args, **kwargs):
        return self._stream.readlines(*args, **kwargs)

    def getvalue(self):
        return self._content

    def seek(self, pos, *args, **kwargs):
        return self._stream.seek(pos, *args, **kwargs)

    def tell(self):
        return self._stream.tell()

    def __iter__(self):
        return iter(self._stream)


def make_csv_file(name="test.csv", content="name,age,city\nAlice,30,NYC\nBob,25,LA\n"):
    """Create a fake CSV uploaded file."""
    return FakeUploadedFile(name, content.encode("utf-8"))


def make_large_file(name="big.csv", size_mb=51):
    """Create a fake file larger than 50MB."""
    content = b"x" * (size_mb * 1024 * 1024)
    return FakeUploadedFile(name, content)


# ─── Setup & Teardown ──────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_uploads():
    """Clean upload directory and ensure local mode before and after each test."""
    # Re-patch config before each test (other test files may change these)
    config.STORAGE_MODE = "local"
    config.UPLOAD_DIR = os.environ["UPLOAD_DIR"]
    upload.UPLOAD_DIR = os.environ["UPLOAD_DIR"]
    ensure_upload_dir()
    yield
    # Clean up files after test
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            os.remove(os.path.join(UPLOAD_DIR, f))


# ─── CSV Validation Tests ─────────────────────────────────

def test_validate_valid_csv():
    """Test that a valid CSV passes validation."""
    file = make_csv_file()
    valid, msg = validate_csv(file)
    assert valid is True
    assert "Valid" in msg


def test_validate_non_csv_extension():
    """Test that non-CSV file extension is rejected."""
    file = make_csv_file(name="data.txt")
    valid, msg = validate_csv(file)
    assert valid is False
    assert "Invalid file type" in msg


def test_validate_xlsx_rejected():
    """Test that .xlsx file is rejected."""
    file = make_csv_file(name="data.xlsx")
    valid, msg = validate_csv(file)
    assert valid is False


def test_validate_json_rejected():
    """Test that .json file is rejected."""
    file = make_csv_file(name="data.json")
    valid, msg = validate_csv(file)
    assert valid is False


def test_validate_oversized_file():
    """Test that files over 50MB are rejected."""
    file = make_large_file(size_mb=51)
    valid, msg = validate_csv(file)
    assert valid is False
    assert "too large" in msg.lower()


def test_validate_invalid_csv_content():
    """Test that unreadable content is rejected."""
    # Use binary content that pandas truly cannot parse as CSV
    bad_bytes = bytes(range(256)) * 10
    file = FakeUploadedFile("bad.csv", bad_bytes)
    valid, msg = validate_csv(file)
    assert valid is False


def test_validate_empty_csv():
    """Test that empty CSV with just headers is valid."""
    file = make_csv_file(content="col1,col2,col3\n")
    valid, msg = validate_csv(file)
    assert valid is True


# ─── File Save Tests ──────────────────────────────────────

def test_save_file_success():
    """Test that saving a CSV file works."""
    file = make_csv_file(name="save_test.csv")
    result = save_file(file)
    assert result["success"] is True
    assert result["filename"] == "save_test.csv"
    assert result["rows"] == 2
    assert result["columns"] == 3
    assert result["storage"] == "local"


def test_save_file_creates_file():
    """Test that save_file creates the file on disk."""
    file = make_csv_file(name="disk_test.csv")
    save_file(file)
    filepath = os.path.join(UPLOAD_DIR, "disk_test.csv")
    assert os.path.exists(filepath)


def test_save_file_correct_size():
    """Test that saved file reports correct size."""
    # Use enough content so size_kb rounds above 0.0
    rows = "\n".join([f"{i},{i*2},{i*3}" for i in range(200)])
    content = "a,b,c\n" + rows + "\n"
    file = make_csv_file(name="size_test.csv", content=content)
    result = save_file(file)
    assert result["size_kb"] > 0


def test_save_file_returns_column_names():
    """Test that save returns correct column names."""
    file = make_csv_file(content="product,sales,region\nA,100,North\n")
    result = save_file(file)
    assert "product" in result["column_names"]
    assert "sales" in result["column_names"]
    assert "region" in result["column_names"]


# ─── File List Tests ──────────────────────────────────────

def test_list_files_empty():
    """Test that list_files returns empty list when no files."""
    files = list_files()
    assert isinstance(files, list)


def test_list_files_after_upload():
    """Test that uploaded file appears in file list."""
    file = make_csv_file(name="listed.csv")
    save_file(file)
    files = list_files()
    filenames = [f["filename"] for f in files]
    assert "listed.csv" in filenames


def test_list_files_only_csv():
    """Test that only CSV files are listed."""
    # Save a CSV
    file = make_csv_file(name="real.csv")
    save_file(file)
    # Create a non-CSV file manually
    with open(os.path.join(UPLOAD_DIR, "notes.txt"), "w") as f:
        f.write("not a csv")
    files = list_files()
    filenames = [f["filename"] for f in files]
    assert "real.csv" in filenames
    assert "notes.txt" not in filenames


# ─── File Loading Tests ───────────────────────────────────

def test_load_file_as_df():
    """Test that load_file_as_df returns a DataFrame."""
    file = make_csv_file(name="loadme.csv")
    save_file(file)
    df = load_file_as_df("loadme.csv")
    assert df is not None
    assert len(df) == 2
    assert "name" in df.columns


def test_load_nonexistent_file():
    """Test that loading non-existent file returns None."""
    df = load_file_as_df("doesnotexist.csv")
    assert df is None


def test_load_file_correct_data():
    """Test that loaded DataFrame has correct values."""
    file = make_csv_file(content="x,y\n10,20\n30,40\n")
    save_file(file)
    df = load_file_as_df(file.name)
    assert df["x"].iloc[0] == 10
    assert df["y"].iloc[1] == 40
