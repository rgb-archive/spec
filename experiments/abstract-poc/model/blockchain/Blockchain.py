from typing import List, Dict

from model.blockchain.Block import Block


class Blockchain:
    def __init__(self, initial_blocks: List[Block]):
        self.index: Dict[int, Block] = {}

        for block in initial_blocks:
            self.index[block.height] = block

    def add_block(self, block: Block):
        self.index[block.height] = block

    def get_range(self, from_block=0, to_block=500000) -> List[Block]:  # TODO: check off-by-one
        return_list: List[Block] = []

        for height in range(from_block, to_block):
            if self.index.get(height):
                return_list.append(self.index[height])

        return return_list
