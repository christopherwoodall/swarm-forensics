"""Offline tests for the download and sample modules. No test uses the network."""

import contextlib
import gzip
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from huggingface_hub.errors import HfHubHTTPError

from swarm_forensics.ingest import download, sample

TOKEN = "hf_secret_test_token"
FILES = {
    ".gitattributes": 10,
    "README.md": 100,
    "SCHEMA.md": 200,
    "events.jsonl.gz": 1000,
    "chat_messages.jsonl.gz": 500,
    "agent_goals.jsonl.gz": 50,
    "village-transcript.json": 2000,
    "images/computer-use-turns/2025-04-02.tar": 10**9,
    "images/computer-use-turns/index.json": 300,
    "screenshot.png": 400,
}


def fake_info(files=FILES, sha="abc123"):
    siblings = [SimpleNamespace(rfilename=path, size=size) for path, size in files.items()]
    return SimpleNamespace(sha=sha, siblings=siblings)


def http_error(status):
    # A stand-in response keeps the tests independent of the HTTP library version.
    response = SimpleNamespace(status_code=status, headers={}, request=None)
    return HfHubHTTPError("failure", response=response)


class SelectionTests(unittest.TestCase):
    def test_default_selection_excludes_images(self):
        selected = download.select_files(FILES)
        self.assertEqual(
            set(selected),
            {
                "README.md",
                "SCHEMA.md",
                "events.jsonl.gz",
                "chat_messages.jsonl.gz",
                "agent_goals.jsonl.gz",
                "village-transcript.json",
            },
        )

    def test_table_selection_returns_only_named_tables(self):
        selected = download.select_files(FILES, ["events", "agent_goals"])
        self.assertEqual(set(selected), {"events.jsonl.gz", "agent_goals.jsonl.gz"})

    def test_unknown_table_is_rejected(self):
        with self.assertRaisesRegex(download.DownloadError, "Unknown table: nope"):
            download.parse_tables(["events", "nope"])

    def test_missing_table_file_is_rejected(self):
        with self.assertRaisesRegex(download.DownloadError, "not found"):
            download.select_files({"README.md": 1}, ["events"])

    def test_pending_bytes_skips_complete_files(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            (dest / "a.bin").write_bytes(b"x" * 10)
            (dest / "b.bin").write_bytes(b"x" * 3)
            pending = download.pending_bytes({"a.bin": 10, "b.bin": 10, "c.bin": 5}, dest)
        self.assertEqual(pending, 15)


class ResolveTests(unittest.TestCase):
    def test_resolve_returns_commit_and_sizes(self):
        with mock.patch.object(download, "HfApi") as api:
            api.return_value.dataset_info.return_value = fake_info()
            sha, files = download.resolve_dataset(TOKEN, "main")
        self.assertEqual(sha, "abc123")
        self.assertEqual(files, FILES)
        api.return_value.dataset_info.assert_called_once_with(
            download.REPO_ID, revision="main", files_metadata=True, token=TOKEN
        )

    def test_denied_access_message_hides_token(self):
        with mock.patch.object(download, "HfApi") as api:
            api.return_value.dataset_info.side_effect = http_error(403)
            with self.assertRaises(download.DownloadError) as context:
                download.resolve_dataset(TOKEN, None)
        self.assertIn("HTTP 403", str(context.exception))
        self.assertNotIn(TOKEN, str(context.exception))


class RunTests(unittest.TestCase):
    def run_command(self, argv, token=TOKEN):
        environment = {"HF_TOKEN": token} if token else {}
        output = io.StringIO()
        errors = io.StringIO()
        with (
            mock.patch.dict("os.environ", environment, clear=True),
            mock.patch.object(download, "HfApi") as api,
            mock.patch.object(download, "hf_hub_download") as fetch,
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(errors),
        ):
            api.return_value.dataset_info.return_value = fake_info()
            code = download.main(argv)
        return code, output.getvalue(), errors.getvalue(), fetch

    def test_missing_token_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            code, _, errors, fetch = self.run_command(["download", "--dest", directory], token="")
        self.assertEqual(code, 1)
        self.assertIn("HF_TOKEN is not set", errors)
        fetch.assert_not_called()

    def test_info_downloads_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            code, output, _, fetch = self.run_command(["info", "--dest", directory])
        self.assertEqual(code, 0)
        self.assertIn("Revision: abc123", output)
        self.assertNotIn(TOKEN, output)
        fetch.assert_not_called()

    def test_download_pins_revision_and_skips_images(self):
        with tempfile.TemporaryDirectory() as directory:
            code, _, _, fetch = self.run_command(["download", "--dest", directory])
            dest = Path(directory)
        self.assertEqual(code, 0)
        requested = {call.args[1] for call in fetch.call_args_list}
        self.assertEqual(requested, set(download.select_files(FILES)))
        for call in fetch.call_args_list:
            self.assertEqual(call.args[0], download.REPO_ID)
            self.assertEqual(call.kwargs["repo_type"], "dataset")
            self.assertEqual(call.kwargs["revision"], "abc123")
            self.assertEqual(call.kwargs["local_dir"], dest)
            self.assertEqual(call.kwargs["token"], TOKEN)

    def test_download_named_tables_only(self):
        with tempfile.TemporaryDirectory() as directory:
            code, _, _, fetch = self.run_command(
                ["download", "--dest", directory, "--tables", "events"]
            )
        self.assertEqual(code, 0)
        self.assertEqual([call.args[1] for call in fetch.call_args_list], ["events.jsonl.gz"])

    def test_unknown_table_downloads_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            code, _, errors, fetch = self.run_command(
                ["download", "--dest", directory, "--tables", "images"]
            )
        self.assertEqual(code, 1)
        self.assertIn("Unknown table", errors)
        fetch.assert_not_called()

    def test_insufficient_disk_space_downloads_nothing(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            mock.patch.object(download, "free_bytes", return_value=10),
        ):
            code, _, errors, fetch = self.run_command(["download", "--dest", directory])
        self.assertEqual(code, 1)
        self.assertIn("Not enough disk space", errors)
        fetch.assert_not_called()

    def test_download_error_hides_token(self):
        output = io.StringIO()
        errors = io.StringIO()
        with (
            tempfile.TemporaryDirectory() as directory,
            mock.patch.dict("os.environ", {"HF_TOKEN": TOKEN}, clear=True),
            mock.patch.object(download, "HfApi") as api,
            mock.patch.object(download, "hf_hub_download", side_effect=http_error(401)),
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(errors),
        ):
            api.return_value.dataset_info.return_value = fake_info()
            code = download.main(["download", "--dest", directory])
        self.assertEqual(code, 1)
        self.assertIn("HTTP 401", errors.getvalue())
        self.assertNotIn(TOKEN, errors.getvalue() + output.getvalue())


class SampleTests(unittest.TestCase):
    def test_sample_tables_stream_line_by_line(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = sample.write_sample(Path(directory), rows=10)
            self.assertEqual(
                {path.name for path in paths},
                {"agent_goals.jsonl.gz", "chat_messages.jsonl.gz", "events.jsonl.gz"},
            )
            with gzip.open(Path(directory) / "events.jsonl.gz", "rt", encoding="utf-8") as handle:
                events = [json.loads(line) for line in handle]
        self.assertEqual([event["event_index"] for event in events], list(range(10)))
        self.assertTrue(all("actionType" in event["data"] for event in events))

    def test_sample_is_deterministic(self):
        self.assertEqual(sample.build_tables(20), sample.build_tables(20))


if __name__ == "__main__":
    unittest.main()
