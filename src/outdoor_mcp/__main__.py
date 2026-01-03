from __future__ import annotations

import asyncio
from .server import OutdoorIntelligenceServer


def main() -> None:
    server = OutdoorIntelligenceServer()

    async def runner():
        try:
            await server.run()
        finally:
            await server.close()

    asyncio.run(runner())


if __name__ == "__main__":
    main()
