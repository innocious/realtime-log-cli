import asyncio
import pytest
from pathlib import Path
from src.file_watcher import tail_file

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

async def test_tail_file_detects_new_lines(tmp_path: Path):
    """
    Tests the core functionality: that tail_file correctly detects and yields
    a new line written to a file after monitoring has started.
    """
    log_file = tmp_path / "test.log"
    log_file.touch() # Create the file

    # Start the tailing task in the background
    tail_task = asyncio.create_task(anext(tail_file(str(log_file))))

    # Give the task a moment to start up and seek to the end of the file
    await asyncio.sleep(0.05)

    # Write a new line to the file
    test_line = "Hello, world!"
    with open(log_file, "a") as f:
        f.write(f"{test_line}\n")

    # The task should now complete and we can get its result
    result = await tail_task

    assert result == test_line

async def anext(async_generator):
    """Helper function to get the next item from an async generator."""
    return await async_generator.__anext__()
