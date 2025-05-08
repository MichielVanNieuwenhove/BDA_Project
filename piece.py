
class Piece:
    def __init__(self, amount_blocks, empty=True):
        self.blocks = [int(not empty)] * amount_blocks
        self.amount_blocks = amount_blocks

    def is_complete(self):
        is_complete = True
        for i in self.blocks:
            if i == 0:
                is_complete = False
                break
        return is_complete

    def get_first_incomplete_idx(self):
        return self.blocks.index(0)

    def set_block(self, idx):
        self.blocks[idx] = 1