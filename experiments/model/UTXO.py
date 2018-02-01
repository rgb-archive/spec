import json


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

    def to_json(self) -> str:
        return json.dumps({
            'txid': self.txid,
            'index': self.index
        }, sort_keys=True)
