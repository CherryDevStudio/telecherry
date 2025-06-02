class DC:
    def __init__(self) -> None:
        self.ipv4 = {
            1: "149.154.175.53",
            2: "149.154.167.51",
            3: "149.154.175.100",
            4: "149.154.167.91",
            5: "91.108.56.130"
        }
    
    def lookup(
        self, 
        dc_id: int, 
        test_mode: bool = False, 
        is_cdn: bool = False
    ) -> str:
        if not test_mode:
            return self.ipv4[dc_id]

        raise ValueError("Testmode is not implemented")
