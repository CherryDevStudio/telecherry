from typing import ClassVar


class DataCenter:
    """A class for getting the address of a Telegram datacenter."""

    IPV4_PRODUCTION: ClassVar[dict[int, str]] = {
        1: "149.154.175.53",
        2: "149.154.167.51",
        3: "149.154.175.100",
        4: "149.154.167.91",
        5: "91.108.56.130",
    }
    IPV4_TEST: ClassVar[dict[int, str]] = {
        1: "149.154.175.10",
        2: "149.154.167.40",
        3: "149.154.175.117",
    }
    IPV6_PRODUCTION: ClassVar[dict[int, str]] = {
        1: "2001:b28:f23d:f001::a",
        2: "2001:67c:4e8:f002::a",
        3: "2001:b28:f23d:f003::a",
        4: "2001:67c:4e8:f004::a",
        5: "2001:b28:f23f:f005::a",
    }
    IPV6_TEST: ClassVar[dict[int, str]] = {
        1: "2001:b28:f23d:f001::e",
        2: "2001:67c:4e8:f002::e",
        3: "2001:b28:f23d:f003::e",
    }

    def __new__(cls, *, dc_id: int, use_ipv6: bool, test_mode: bool) -> str:
        """Return the IP address of the Telegram data center connection.

        Args:
            dc_id (int): datacenter id
            use_ipv6 (bool): are you using ipv6 or not
            test_mode (bool): test mode or not

        Returns:
            str: connection IP address
        """
        if use_ipv6 and test_mode:
            return DataCenter.IPV6_TEST[dc_id]

        if use_ipv6:
            return DataCenter.IPV6_PRODUCTION[dc_id]

        if test_mode:
            return DataCenter.IPV4_TEST[dc_id]

        return DataCenter.IPV4_PRODUCTION[dc_id]
