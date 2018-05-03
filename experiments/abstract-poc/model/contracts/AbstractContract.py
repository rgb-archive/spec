import hashlib
from typing import Dict

from model.blockchain.UTXO import UTXO
from protobuf import rgb_pb2


class AbstractContract:
    def __init__(self, title: str, issuance_utxo: UTXO, total_supply: int):
        assert total_supply > 0, "Max supply must be > 0"
        assert total_supply < 2 ** 64, "Max supply is 2^64 - 1"
        assert issuance_utxo.known_txid(), "The issuance UTXO must be entirely specified"

        self.title = title
        self.issuance_utxo = issuance_utxo
        self.total_supply = total_supply

    def get_token_id(self) -> str:
        hash_object = hashlib.sha256(self.serialize_to_string())
        return hash_object.hexdigest()

    @staticmethod
    def deserialize_from_string(data: str) -> 'AbstractContract':
        from model.contracts.Contract import Contract
        from model.contracts.CrowdsaleContract import CrowdsaleContract

        contract = rgb_pb2.Contract()
        contract.ParseFromString(data)

        contracts_map: Dict[str, AbstractContract] = {
            'generic_contract': Contract,
            'crowdsale_contract': CrowdsaleContract
        }

        if not contracts_map.get(contract.type):
            raise Exception('Unknown contract type "{}"'.format(contract.type))

        return contracts_map[contract.type].deserialize(contract)

    def serialize_to_string(self) -> bytes:
        return self.serialize().SerializeToString()

    def verify(self) -> bool:
        # TODO: verify the commitment on the blockchain

        return self.issuance_utxo.spent

    # Templates for child classes

    def get_type(self) -> str:
        raise Exception('Trying to get the typename from an abstract contract')

    @staticmethod
    def deserialize(pb_contract: rgb_pb2.Contract) -> 'AbstractContract':
        raise Exception('Cannot deserialize an abstract contract')

    def serialize(self) -> rgb_pb2.Contract:
        raise Exception('Cannot serialize an abstract contract')

    def __str__(self):
        return 'Contract (type="{}") "{}", token id = {}\n' \
               'Committed to UTXO {}\n' \
               'Total issuance of {}'.format(self.title, self.get_type(), self.get_token_id(),
                                             self.issuance_utxo, self.total_supply)
