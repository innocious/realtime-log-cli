import asyncio
import pytest
from pathlib import Path
from typing import AsyncGenerator, List

from src.file_watcher import tail_file

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    """A pytest fixture that creates a temporary log file for testing."""
    file_path = tmp_path / "test.log"
    file_path.touch()
    return file_path

async def collect_n_lines(gen: AsyncGenerator[str, None], n: int) -> List[str]:
    """Helper to collect a specific number of lines from an async generator."""
    lines = []
    for _ in range(n):
        try:
            # Set a timeout to prevent tests from hanging indefinitely
            lines.append(await asyncio.wait_for(gen.__anext__(), timeout=1.0))
        except asyncio.TimeoutError:
            break
    return lines

async def test_tail_file_detects_single_line(log_file: Path):
    """
    Tests the core functionality: that tail_file correctly detects and yields
    a new line written to a file after monitoring has started.
    """
    tailer = tail_file(str(log_file))

    # Start collecting the line in the background. This lets the tailer start.
    collection_task = asyncio.create_task(collect_n_lines(tailer, 1))
    # Give the event loop a tick to run the tailer's initial setup.
    await asyncio.sleep(0.01)

    # Now, with the tailer active, write a new line to the file.
    test_line = "A single new line"
    with open(log_file, "a") as f:
        f.write(f"{test_line}\n")

    # Await the result from our background collection task.
    lines = await collection_task

    assert lines == [test_line]

async def test_tail_file_detects_multiple_lines(log_file: Path):
    """
    Tests that the tailer can correctly detect and yield multiple lines
    written in quick succession.
    """
    tailer = tail_file(str(log_file))
    test_lines = ["Line 1", "Line 2", "Line 3"]

    # Start collecting lines in the background.
    collection_task = asyncio.create_task(collect_n_lines(tailer, len(test_lines)))
    await asyncio.sleep(0.01)

    # Write multiple new lines to the file.
    with open(log_file, "a") as f:
        for line in test_lines:
            f.write(f"{line}\n")

    # Await the collected lines.
    lines = await collection_task

    assert lines == test_lines

async def test_tail_file_ignores_pre_existing_content(log_file: Path):
    """
    Tests that the tailer starts from the end of the file and does not
    re-read content that was already there.
    """
    # Write initial content BEFORE starting the tailer
    with open(log_file, "a") as f:
        f.write("This is old content.\n")

    tailer = tail_file(str(log_file))
    new_line = "This is the new line to be detected"

    # Start collecting in the background.
    collection_task = asyncio.create_task(collect_n_lines(tailer, 1))
    await asyncio.sleep(0.01)

    # Write a new line AFTER starting the tailer.
    with open(log_file, "a") as f:
        f.write(f"{new_line}\n")

    # We should only get the new line.
    lines = await collection_task

    assert lines == [new_line]
    assert "This is old content." not in lines

