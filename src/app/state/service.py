import asyncio
import hashlib


async def sha256_digest(data: bytes) -> str:
    """Compute the SHA-256 hash of the given bytes in a separate thread."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: hashlib.sha256(data).hexdigest())
