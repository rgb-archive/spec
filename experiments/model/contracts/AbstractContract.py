import hashlib
import json
from typing import Dict

from model.UTXO import UTXO


class AbstractContract:
    def __init__(self, title: str, issuance_utxo: UTXO, total_supply: int):
        assert total_supply > 0, "Max supply must be > 0"
        assert total_supply < 2 ** 64, "Max supply is 2^64 - 1"
        assert issuance_utxo.known_txid(), "The issuance UTXO must be entirely specified"

        self.title = title
        self.issuance_utxo = issuance_utxo
        self.total_supply = total_supply

    def get_token_id(self) -> str:
        hash_object = hashlib.sha256(self.to_json().encode('utf-8'))
        return hash_object.hexdigest()

    @staticmethod
    def from_json(string: str) -> 'AbstractContract':
        from model.contracts.Contract import Contract
        from model.contracts.CrowdsaleContract import CrowdsaleContract

        obj = json.loads(string)

        contracts_map: Dict[str, AbstractContract] = {
            'generic_contract': Contract,
            'crowdsale_contract': CrowdsaleContract
        }

        if not contracts_map.get(obj['type']):
            raise Exception('Unknown contract type "{}"'.format(obj['type']))

        return contracts_map[obj['type']].from_json_obj(obj)

    # Templates for child classes

    def get_type(self) -> str:
        raise Exception('Trying to get the typename from an abstract contract')

    @staticmethod
    def from_json_obj(obj: Dict) -> 'AbstractContract':
        raise Exception('Cannot deserialize an abstract contract')

    def to_json(self) -> str:
        raise Exception('Cannot serialize an abstract contract')

    def verify(self) -> bool:
        raise Exception('Cannot verify an abstract contract')

    def __str__(self):
        return 'Contract (type="{}") "{}", token id = {}\n' \
               'Committed to UTXO {}\n' \
               'Total issuance of {}'.format(self.title, self.get_type(), self.get_token_id(),
                                             self.issuance_utxo, self.total_supply)
