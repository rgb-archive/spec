from model.UTXO import UTXO
from model.contracts.AbstractContract import AbstractContract


class CrowdsaleContract(AbstractContract):
    def __init__(self, title: str, issuance_utxo: UTXO, total_supply: int):
        super().__init__(title, issuance_utxo, total_supply)

        # TODO
