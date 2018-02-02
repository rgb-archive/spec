from typing import Dict


class UTXO:
    def __init__(self, txid: str or None, index: int, spent: bool = False):
        assert index >= 0, "The UTXO index must be positive"

        if txid == '':
            txid = None

        self.txid = txid
        self.index = index
        self.spent = spent

    def known_txid(self) -> bool:
        return self.txid is not None

    def spend(self):
        if self.spent:
            raise Exception('UTXO {} has already been spent'.format(self))

        self.spent = True

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

    def __str__(self) -> str:
        return 'UTXO<{}:{}>'.format(self.txid, self.index)

    def to_dict(self) -> Dict[str, str or int]:
        return {
            'txid': self.txid,
            'index': self.index
        }
