import hashlib
import json

from model.UTXO import UTXO


class Contract:
    def __init__(self, title: str, issuance_utxo: UTXO, owner_utxo: UTXO, total_supply: int):
        assert total_supply > 0, "Max supply must be > 0"
        assert total_supply < 2 ** 64, "Max supply is 2^64 - 1"
        assert issuance_utxo.known_txid(), "The issuance UTXO must be entirely specified"

        self.title = title
        self.issuance_utxo = issuance_utxo
        self.owner_utxo = owner_utxo
        self.total_supply = total_supply

    def get_token_id(self) -> str:
        hash_object = hashlib.sha256(self.to_json().encode('utf-8'))
        return hash_object.hexdigest()

    def to_json(self) -> str:
        return json.dumps({
            'title': self.title,
            'issuance_utxo': self.issuance_utxo.__dict__,
            'owner_utxo': self.owner_utxo.__dict__,
            'total_supply': self.total_supply
        }, sort_keys=True)
