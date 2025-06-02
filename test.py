import io
import os
import asyncio
import logging

from telecherry.network.transport import TCPAbridged


class ReqPQMulti:
    def __init__(self, nonce: int) -> None:
        self.nonce = nonce
    
    def to_bytes(self) -> bytes:
        buffer = io.BytesIO()
        buffer.write(0xbe7e8ef1.to_bytes(4, "little"))
        buffer.write(self.nonce.to_bytes(16, "little", signed=True))
        return buffer.getvalue()


logger = logging.getLogger("telecherry.logger")
logging.basicConfig(
    level="DEBUG"
)


async def main():
    tcp = await TCPAbridged.connect(dc_id=2)
    packet = ReqPQMulti(
        nonce=int.from_bytes(os.urandom(16), "little", signed=True)
    )

    await tcp.send(packet.to_bytes())
    data = await tcp.receive()

    if data:
        print([int(x) for x in data])


asyncio.run(main())
