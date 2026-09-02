import pytest
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend


@pytest.fixture(autouse=True)
async def _init_cache():
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")
    yield
    await FastAPICache.clear()
