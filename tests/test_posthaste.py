import subprocess
import sys
import os
import tempfile
import time
import platform
import re
import pytest

SERVER_URL = "http://localhost:7777"

def start_local_server():
    """Start a local haste-server."""
    command = ['haste-server', '--port', '7777']
    if platform.system() == 'Windows':
        command = ['haste-server.cmd', '--port', '7777']
    
    server_proc = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True  # VERY important on Windows
    )
    time.sleep(1)  # give it a second to boot
    return server_proc

def stop_local_server(proc):
    """Stop the local haste-server."""
    proc.terminate()
    proc.wait()

# ----------------------------------------------------------------------
# Pytest fixture: Start server ONCE for all tests
# ----------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def local_server():
    server = start_local_server()
    yield server
    stop_local_server(server)

# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_upload_from_stdin():
    """Test piping text input into posthaste."""
    result = subprocess.run(
        [sys.executable, '-m', 'posthaste'],
        input=b"Hello from test!",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "POSTHASTE_URL": SERVER_URL}
    )
    assert result.returncode == 0
    assert SERVER_URL.encode() in result.stdout

def test_upload_from_file():
    """Test uploading from a file."""
    with tempfile.NamedTemporaryFile('w+', delete=False) as tmpfile:
        tmpfile.write("Temporary file test!")
        tmpfile_path = tmpfile.name

    try:
        result = subprocess.run(
            [sys.executable, '-m', 'posthaste', tmpfile_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "POSTHASTE_URL": SERVER_URL}
        )
        assert result.returncode == 0
        assert SERVER_URL.encode() in result.stdout
    finally:
        os.remove(tmpfile_path)

def test_error_on_no_input():
    """Test running with no stdin and no file."""
    result = subprocess.run(
        [sys.executable, '-m', 'posthaste'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=b''
    )
    assert result.returncode != 0
    assert b"No input provided." in result.stderr

def test_upload_invalid_file():
    """Test uploading a nonexistent file."""
    result = subprocess.run(
        [sys.executable, '-m', 'posthaste', 'nonexistentfile.txt'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    assert result.returncode != 0
    assert b"No such file" in result.stderr or b"Error" in result.stderr

def test_upload_invalid_server():
    """Test uploading to a dead server."""
    result = subprocess.run(
        [sys.executable, '-m', 'posthaste'],
        input=b"Testing bad server!",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "POSTHASTE_URL": "http://localhost:9999"}
    )
    assert result.returncode != 0
    assert b"Failed to connect" in result.stderr or b"Connection refused" in result.stderr

def test_upload_empty_file():
    """Test uploading an empty file."""
    with tempfile.NamedTemporaryFile('w+', delete=False) as tmpfile:
        tmpfile_path = tmpfile.name

    try:
        result = subprocess.run(
            [sys.executable, '-m', 'posthaste', tmpfile_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "POSTHASTE_URL": SERVER_URL}
        )
        assert result.returncode != 0
        assert b"empty" in result.stderr
    finally:
        os.remove(tmpfile_path)

def test_upload_returns_valid_key():
    """Test that uploading text returns a valid key URL."""
    result = subprocess.run(
        [sys.executable, '-m', 'posthaste'],
        input=b"Testing key format!",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "POSTHASTE_URL": SERVER_URL}
    )
    assert result.returncode == 0
    output = result.stdout.decode()
    assert re.search(r"http://localhost:7777/share/\w+", output)

def test_upload_large_file():
    """Test uploading a large file."""
    big_content = "A" * (300 * 1024)  # 300 KB of 'A'
    with tempfile.NamedTemporaryFile('w+', delete=False) as tmpfile:
        tmpfile.write(big_content)
        tmpfile_path = tmpfile.name

    try:
        result = subprocess.run(
            [sys.executable, '-m', 'posthaste', tmpfile_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "POSTHASTE_URL": SERVER_URL}
        )
        assert result.returncode == 0
        assert SERVER_URL.encode() in result.stdout
    finally:
        os.remove(tmpfile_path)

def test_upload_custom_server_url():
    """Test uploading with a different POSTHASTE_URL."""
    result = subprocess.run(
        [sys.executable, '-m', 'posthaste'],
        input=b"Hello from custom URL test!",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "POSTHASTE_URL": "http://127.0.0.1:7777"}
    )
    assert result.returncode == 0
    output = result.stdout.decode()
    assert "http://127.0.0.1:7777" in output

def test_help_message():
    """Test that the help message is displayed."""
    result = subprocess.run(
        [sys.executable, '-m', 'posthaste', '--help'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    assert result.returncode == 0
    output = result.stdout.decode()
    assert "usage" in output.lower() or "help" in output.lower()

def test_upload_timeout():
    """Test that a timeout is handled gracefully."""
    # 10.255.255.1 is an unroutable IP, so connection will hang/fail
    fake_server_url = "http://10.255.255.1:7777"
    
    result = subprocess.run(
        [sys.executable, '-m', 'posthaste'],
        input=b"Testing timeout behavior!",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,  # Max time for the subprocess itself to exist
        env={**os.environ, "POSTHASTE_URL": fake_server_url}
    )
    
    assert result.returncode != 0
    stderr = result.stderr.decode().lower()
    assert "timeout" in stderr or "failed to connect" in stderr or "connection refused" in stderr
