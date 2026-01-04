import pytest


@pytest.mark.asyncio
async def test_import_server():
    from outdoor_mcp.server import OutdoorIntelligenceServer

    srv = OutdoorIntelligenceServer()
    try:
        assert srv.mcp is not None
    finally:
        await srv.close()
