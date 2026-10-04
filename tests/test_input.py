import errno
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from local_input import read_local_file


class InputTests(unittest.TestCase):
    def test_stream_creation_failure_closes_descriptor(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input"
            path.write_bytes(b"local data")
            opened = []

            def fail_stream(descriptor, *args, **kwargs):
                opened.append(descriptor)
                raise OSError("stream creation failed")

            with mock.patch("local_input.os.fdopen", side_effect=fail_stream):
                with self.assertRaisesRegex(OSError, "stream creation failed"):
                    read_local_file(path)

            self.assertEqual(len(opened), 1)
            try:
                os.fstat(opened[0])
            except OSError as error:
                self.assertEqual(error.errno, errno.EBADF)
            else:
                os.close(opened[0])
                self.fail("input descriptor remained open after stream creation failed")

    def test_stream_creation_failure_preserves_original_error(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input"
            path.write_bytes(b"local data")

            def fail_after_closing(descriptor, *args, **kwargs):
                os.close(descriptor)
                raise OSError("original stream failure")

            with mock.patch("local_input.os.fdopen", side_effect=fail_after_closing):
                with self.assertRaisesRegex(OSError, "original stream failure"):
                    read_local_file(path)

    def test_oversized_link_and_nonregular_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            path=root/"input"
            path.write_bytes(b"x"*9)
            with self.assertRaises(ValueError): read_local_file(path,8)
            link=root/"link"
            link.symlink_to(path)
            with self.assertRaises(ValueError): read_local_file(link)
            with self.assertRaises((ValueError,OSError)): read_local_file(root)
            if hasattr(os,"mkfifo"):
                pipe=root/"pipe"
                os.mkfifo(pipe)
                with self.assertRaises(ValueError): read_local_file(pipe)

    def test_ambiguous_and_deep_json_rejected(self):
        from strict_json import loads
        for value in ('{"setting":true,"setting":false}', '{"number":NaN}', '['*2000+'0'+']'*2000):
            with self.subTest(value=value[:40]),self.assertRaises(ValueError): loads(value)
