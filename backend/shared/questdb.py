"""QuestDB connection — ILP ingestion and REST query interface."""

import socket
from datetime import datetime

import aiohttp
import structlog

from shared.config import settings

logger = structlog.get_logger()


class QuestDBClient:
    """QuestDB client supporting ILP ingestion and REST queries."""

    def __init__(self):
        self.ilp_host = settings.questdb_host
        self.ilp_port = settings.questdb_ilp_port
        self.rest_url = f"http://{settings.questdb_host}:{settings.questdb_rest_port}"
        self._socket: socket.socket | None = None

    def _get_socket(self) -> socket.socket:
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.ilp_host, self.ilp_port))
            logger.info("QuestDB ILP socket connected", host=self.ilp_host, port=self.ilp_port)
        return self._socket

    def send_ilp(self, table: str, tags: dict, fields: dict, timestamp: datetime | None = None) -> None:
        """Send a single row via InfluxDB Line Protocol."""
        sock = self._get_socket()
        tag_str = ",".join(f"{k}={v}" for k, v in tags.items())
        field_str = ",".join(f"{k}={v}" for k, v in fields.items())
        ts = int((timestamp or datetime.utcnow()).timestamp() * 1_000_000_000)
        line = f"{table},{tag_str} {field_str} {ts}\n"
        sock.sendall(line.encode())

    async def query(self, sql: str) -> dict:
        """Execute a SQL query via REST API."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.rest_url}/exec", params={"query": sql}) as resp:
                return await resp.json()

    async def health(self) -> dict:
        """Health check via REST API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.rest_url}/exec", params={"query": "SELECT 1"}) as resp:
                    if resp.status == 200:
                        return {"status": "healthy"}
                    return {"status": "unhealthy", "code": resp.status}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def close(self) -> None:
        if self._socket:
            self._socket.close()
            self._socket = None
            logger.info("QuestDB ILP socket closed")


questdb = QuestDBClient()
