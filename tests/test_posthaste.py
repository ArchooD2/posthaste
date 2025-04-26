import subprocess
import sys
import os
import tempfile
import time
import platform
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

def test_upload_from_stdin():
    """Test piping text input into posthaste."""
    server = start_local_server()
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'posthaste'],
            input=b"Hello from test!",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "POSTHASTE_URL": SERVER_URL}
        )
        assert result.returncode == 0
        assert SERVER_URL.encode() in result.stdout
    finally:
        stop_local_server(server)

def test_upload_from_file():
    """Test uploading from a file."""
    server = start_local_server()
    try:
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
    finally:
        stop_local_server(server)

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

