import asyncio
import ipaddress
import logging
import socket
from typing import Any

import jsonschema
import socks  # pyright: ignore[reportMissingTypeStubs]

log = logging.getLogger(__name__)

PROXY_TYPES = {
    "socks4": 1,
    "socks5": 2,
    "http": 3,
}
PROXY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "proxy_type": {
            "type": "string",
            "enum": ["socks4", "socks5", "http"],
        },
        "addr": {"type": "string"},
        "port": {"type": "integer"},
        "username": {"type": "string"},
        "password": {"type": "string"},
    },
    "required": ["proxy_type", "addr", "port"],
}


class TCPAbridged:
    """TCP Abridged MTProto transport."""

    PACKET_LENGTH = 127
    TIMEOUT = 10
    PORT = 443

    def __init__(
        self,
        *,
        use_ipv6: bool,
        proxy: dict[str, Any] | None = None,
    ) -> None:
        self.proxy = proxy
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.socket: socks.socksocket | socket.socket | None = None

        if proxy:
            host: str = proxy.get("addr", "")

            try:
                jsonschema.validate(instance=proxy, schema=PROXY_SCHEMA)

                address = ipaddress.ip_address(address=host)

            except (jsonschema.ValidationError, ValueError):
                log.exception("An incorrect proxy was received")

                self.socket = socks.socksocket(
                    family=socket.AF_INET,
                )

            else:
                if isinstance(address, ipaddress.IPv6Address):
                    self.socket = socks.socksocket(
                        family=socket.AF_INET6,
                    )

                else:
                    self.socket = socks.socksocket(
                        family=socket.AF_INET,
                    )

                log.info("Proxy connected %s", host)

                proxy["proxy_type"] = PROXY_TYPES.get(proxy["proxy_type"])

                self.socket.set_proxy(**proxy)  # pyright: ignore[reportUnknownMemberType]
                self.socket.settimeout(timeout=TCPAbridged.TIMEOUT)  # pyright: ignore[reportUnknownMemberType]

        else:
            self.socket = socket.socket(
                socket.AF_INET6 if use_ipv6 else socket.AF_INET,
            )

            self.socket.setblocking(False)  # noqa: FBT003

    async def _raw_send(self, data: bytes) -> None:
        if self.writer is not None:
            self.writer.write(data)

            await self.writer.drain()

        else:
            msg = "Connect before sending"

            raise ConnectionError(msg)

    async def connect(self, address: str) -> None:
        """Connect to the Telegram server.

        Args:
            address (str): address of DC server.
        """
        if self.socket is not None:
            if self.proxy:
                self.socket.connect((address, TCPAbridged.PORT))  # pyright: ignore[reportUnknownMemberType]

            else:
                loop = asyncio.get_event_loop()

                await asyncio.wait_for(
                    fut=loop.sock_connect(
                        sock=self.socket,
                        address=(address, TCPAbridged.PORT),
                    ),
                    timeout=TCPAbridged.TIMEOUT,
                )

        self.reader, self.writer = await asyncio.wait_for(
            fut=asyncio.open_connection(
                host=address,
                port=TCPAbridged.PORT,
            ),
            timeout=TCPAbridged.TIMEOUT,
        )

        await self._raw_send(data=b"\xef")

        log.info("Connection created")

    async def send(self, data: bytes) -> None:
        """Send the data to the Telegram server.

        Args:
            data (bytes): payload
        """
        length = len(data) // 4

        if length < TCPAbridged.PACKET_LENGTH:
            await self._raw_send(
                data=bytes([length]) + data,
            )

        else:
            await self._raw_send(
                data=b"\x7f" + length.to_bytes(3, "little") + data,
            )

    async def receive(self) -> bytes:
        """Get the data from the telegram server.

        Raises:
            ConnectionError: Connect before sending

        Returns:
            bytes | None: Response from the server
        """
        if self.reader is not None:
            length = await self.reader.read(1)

            if length == b"\x7f":
                length = await self.reader.read(3)

            return await self.reader.read(int.from_bytes(length, "little") * 4)

        msg = "Connect before sending"

        raise ConnectionError(msg)

    async def close(self) -> None:
        """Close the current connection with the Telegram server."""
        if self.writer is not None:
            self.writer.close()

            await asyncio.wait_for(
                fut=self.writer.wait_closed(),
                timeout=TCPAbridged.TIMEOUT,
            )
