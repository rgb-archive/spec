class UTXO:
    def __init__(self, txid: str, index: int):
        assert index >= 0, "The UTXO index must be positive"

        if txid == '':
            txid = None

        self.txid = txid
        self.index = index

    def known_txid(self) -> bool:
        return self.txid is not None

    @staticmethod
    def from_string(string: str) -> 'UTXO':
        parts = string.split(':')
        return UTXO(parts[0] if parts[0] != '' else None, int(parts[1]))

    @staticmethod
    def from_dict(in_dict):
        return UTXO(in_dict['txid'], in_dict['index'])

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.txid == other.txid and self.index == other.index

        return False
