from __future__ import annotations

import asyncio
import logging
from typing import (
    Optional
)

from .dc import DC


CONNECT_TIMEOUT: float = 10.0
logger = logging.getLogger("telecherry.logger")


class TCPAbridged:
    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        self.reader = reader
        self.writer = writer

    @classmethod
    async def connect(cls, dc_id: int, test_mode: bool = False) -> TCPAbridged:
        dc_resolver = DC()
        ipv4 = dc_resolver.lookup(dc_id, test_mode)

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(
                host=ipv4,
                port=443,
            ),
            timeout=CONNECT_TIMEOUT
        )

        writer.write(b"\xef")
        await writer.drain()

        logger.debug(f"Connection to {ipv4} created")

        return cls(reader, writer)
    
    async def _raw_send(self, payload: bytes) -> None:
        self.writer.write(payload)

        await self.writer.drain()

    async def send(self, payload: bytes) -> None:
        length = len(payload) // 4

        if length < 127:
            await self._raw_send(
                bytes([length]) + payload
            )

        else:
            await self._raw_send(
                b"\x7f" + length.to_bytes(3, "little") + payload
            )

    async def receive(self) -> Optional[bytes]:
        length = await self.reader.read(1)
        
        if length == b"\x7f":
            length = await self.reader.read(3)
        
        return await self.reader.read(int.from_bytes(length, "little") * 4)
