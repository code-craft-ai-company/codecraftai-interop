import os
import tempfile

import ccai.testbase as testbase
from ccai.testbase.mocking import create_module_patch
from ccai.interop.protocols.ssh import sshhelpers
from ccai.interop.protocols.ssh.sshhelpers import (
    lookup_entry_type,
    primitive_parse_directory_listing,
    primitive_directory_exists,
    primitive_file_exists,
    primitive_file_pull,
    primitive_file_push,
    ssh_execute_command_in_channel,
)
from ccai.interop.protocols.ssh.sshconst import INTERACTIVE_PROMPT_BYTES
import stat


class DummySFTPAttr:
    def __init__(self, mode):
        self.st_mode = mode
        self.st_uid = 1000
        self.st_gid = 1000
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0


def test_lookup_entry_type():
    file_attr = DummySFTPAttr(stat.S_IFREG)
    dir_attr = DummySFTPAttr(stat.S_IFDIR)
    link_attr = DummySFTPAttr(stat.S_IFLNK)
    char_attr = DummySFTPAttr(stat.S_IFCHR)
    block_attr = DummySFTPAttr(stat.S_IFBLK)

    testbase.assert_equal(lookup_entry_type("/", "f", file_attr), "file")
    testbase.assert_equal(lookup_entry_type("/", "d", dir_attr), "dir")
    testbase.assert_equal(lookup_entry_type("/", "l", link_attr), "link")
    testbase.assert_equal(lookup_entry_type("/", "c", char_attr), "char")
    testbase.assert_equal(lookup_entry_type("/", "b", block_attr), "block")
    return


def test_primitive_parse_directory_listing():
    content = (
        "drwxr-xr-x 2 user group 4096 Jul 4 00:37 dir1\n"
        "-rw-r--r-- 1 user group  123 Jul 4 00:37 file1\n"
        "lrwxrwxrwx 1 user group   10 Jul 4 00:37 link1 -> /tmp/target\n"
    )
    entries = primitive_parse_directory_listing("/", content)
    testbase.assert_equal(entries["dir1"]["type"], "dir")
    testbase.assert_equal(entries["file1"]["type"], "file")
    testbase.assert_equal(entries["link1"]["type"], "link")
    testbase.assert_equal(entries["link1"]["name"], "link1")
    return


class DummyChannel:
    def __init__(self, stdout_chunks, stderr_chunks=None):
        self.sent = []
        self.in_buffer = DummyPipe(stdout_chunks)
        self.in_stderr_buffer = DummyPipe(stderr_chunks or [])

    def sendall(self, data):
        self.sent.append(data)


class DummyPipe:
    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.index = 0

    def read(self, nbytes, timeout):
        if self.index >= len(self.chunks):
            raise sshhelpers.paramiko.buffered_pipe.PipeTimeout()
        out = self.chunks[self.index]
        self.index += 1
        return out


def test_ssh_execute_command_in_channel_success():
    chunks = [
        b"cmd\n", b"out\n" + INTERACTIVE_PROMPT_BYTES,
        b"echo $?\n", b"0\n" + INTERACTIVE_PROMPT_BYTES,
    ]
    chan = DummyChannel([chunks[0] + chunks[1]], [])
    # For the recursive status check call, use second set of chunks
    status_chunks = [chunks[2] + chunks[3]]
    chan_status = DummyChannel(status_chunks, [])

    # Patch status helper so that the exit-status check uses the dedicated status channel
    def status_side_effect(channel, *, read_timeout, inactivity_timeout, inactivity_interval, chunk_size):
        status_stdout_buffer, status_stderr_buffer = sshhelpers._ssh_execute_command_in_channel_imp(
            chan_status, "echo $?", read_timeout, inactivity_timeout, inactivity_interval, chunk_size
        )
        status_stdout, _ = sshhelpers._process_channel_output("echo $?", status_stdout_buffer, status_stderr_buffer)
        return int(status_stdout)

    with create_module_patch(sshhelpers, "_get_exit_status_in_channel") as mock_status:
        mock_status.configure(side_effect=status_side_effect)
        status, stdout, stderr = ssh_execute_command_in_channel(chan, "cmd", read_timeout=0.1)
    testbase.assert_equal(status, 0)
    testbase.assert_equal(stdout, "out")
    testbase.assert_equal(stderr, "")
    return


def test_primitive_directory_exists_and_file_exists():
    with create_module_patch(sshhelpers, "ssh_execute_command") as mock_exec:
        mock_exec.configure(return_value=(0, "exists\n", ""))
        testbase.assert_equal(primitive_directory_exists(None, "/tmp"), True)
        testbase.assert_equal(primitive_file_exists(None, "/tmp/x"), True)
        mock_exec.configure(return_value=(1, "", "err"))
        testbase.assert_equal(primitive_directory_exists(None, "/tmp"), False)
        testbase.assert_equal(primitive_file_exists(None, "/tmp/x"), False)
    return


def test_primitive_file_pull_and_push():
    with tempfile.TemporaryDirectory() as tdir:
        local_in = os.path.join(tdir, "in.txt")
        local_out = os.path.join(tdir, "out.txt")
        with open(local_in, "w") as f:
            f.write("content")

        calls = []

        def fake_exec(client, command, **kwargs):
            calls.append((command, kwargs))
            if command.startswith("cat >"):
                return 0, b"", b""
            return 0, b"content", b""

        with create_module_patch(sshhelpers, "ssh_execute_command") as mock_exec:
            mock_exec.configure(side_effect=fake_exec)
            primitive_file_pull(None, "remote", local_out)
            primitive_file_push(None, local_in, "remote")

        with open(local_out) as f:
            outdata = f.read()

        testbase.assert_equal(outdata, "content")
        testbase.assert_equal(calls[0][0], "cat remote")
        testbase.assert_equal(calls[1][0], "cat > remote")
    return
