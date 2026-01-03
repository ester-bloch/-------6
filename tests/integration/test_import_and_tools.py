def test_import_server():
    from outdoor_mcp.server import OutdoorIntelligenceServer
    srv = OutdoorIntelligenceServer()
    assert srv.mcp is not None
