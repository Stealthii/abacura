"""Telnet Options handler module"""

from __future__ import annotations

from abc import abstractmethod

SB = b"\xfa"
SE = b"\xf0"
WILL = b"\xfb"
WONT = b"\xfc"
DO = b"\xfd"
DONT = b"\xfe"
IAC = b"\xff"
GA = b"\xf9"


class TelnetOption:
    """Base class for Telnet Option handling"""

    code: int = 0
    name: str = "TelnetOption"

    def do(self) -> None:
        """IAC DO handler"""

    def dont(self) -> None:
        """IAC DONT handler"""

    def will(self) -> None:
        """IAC WILL handler"""

    def wont(self) -> None:
        """IAC WONT handler"""

    @abstractmethod
    def sb(self, sb: bytes) -> None:
        """IAC SB handler"""
