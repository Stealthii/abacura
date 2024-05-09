"""TERMINAL-TYPE SUPPORT"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual import log

from abacura.mud.options import IAC, SB, SE, WILL, TelnetOption

if TYPE_CHECKING:
    from asyncio.streams import StreamWriter

SEND = b"\x01"
IS = b"\x00"
TTYPE = b"\x18"


class TerminalTypeOption(TelnetOption):
    """Base class for Telnet Option handling"""

    code: int = 24
    name: str = "TerminalType"

    def __init__(self, writer: StreamWriter) -> None:
        self.writer = writer
        self.count = 0

    def do(self) -> None:
        """IAC DO handler"""
        self.writer.write(IAC + WILL + TTYPE)
        log.warning("IAC WILL TTYPE")

    def sb(self, sb: bytes) -> None:
        """IAC SB handler"""
        log.debug(f"TTYPE SB RECEIVED: {sb} on {self.count}")
        if sb[1:2] == SEND:
            if self.count == 0:
                self.writer.write(IAC + SB + TTYPE + IS + b"ABACURA PRERELEASE" + IAC + SE)
                self.count = 1
            elif self.count == 1:
                self.writer.write(IAC + SB + TTYPE + IS + b"XTERM-256COLOR" + IAC + SE)
                self.count = 2
            else:
                self.writer.write(IAC + SB + TTYPE + IS + b"MTTS 2831" + IAC + SE)
