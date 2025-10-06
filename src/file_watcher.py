import asyncio
from typing import AsyncGenerator

async def tail_file(filepath: str) -> AsyncGenerator[str, None]:
    """
    Asynchronously monitors a file for new lines, yielding them as they are
    written. This function is non-blocking and recreates the behavior of
    'tail -f'.

    Args:
        filepath: The full path to the file to monitor.

    Yields:
        The next new line found in the file, stripped of whitespace.
    """
    try:
        with open(filepath, 'r') as f:
            # Move to the end of the file
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    # No new line, so we wait asynchronously
                    await asyncio.sleep(0.1)
                    continue
                yield line.strip()
    except FileNotFoundError:
        print(f"File not found: {filepath}. Waiting for it to be created.")
        # Wait for the file to be created
        while True:
            try:
                with open(filepath, 'r') as f:
                    # File has been created, start tailing
                    break
            except FileNotFoundError:
                await asyncio.sleep(1)
        # Restart the tailing process now that the file exists
        async for line in tail_file(filepath):
            yield line
