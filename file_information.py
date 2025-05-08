from piece import Piece
import global_vars

import random

class FileInformation:
    def __init__(self, torrent_file, amount_pieces, empty=True):
        piece_length = torrent_file.info["piece_length"]
        block_size = global_vars.block_size

        self.blocks_per_piece = piece_length // block_size
        total_length = torrent_file.info["length"]
        last_piece_length = total_length - piece_length * (amount_pieces - 1)
        self.blocks_last_piece = (last_piece_length + block_size - 1) // block_size  # ceil division

        self.pieces = [Piece(self.blocks_per_piece, empty) for _ in range(amount_pieces - 1)]
        self.pieces.append(Piece(self.blocks_last_piece, empty))

        self.last_announce = -100
        self.torrent_file = torrent_file

    def get_incomplete_pieces(self):
        incomplete_pieces = []
        for piece in self.pieces:
            if not piece.is_complete():
                incomplete_pieces.append(piece)

        return incomplete_pieces

    def get_random_incomplete_piece(self):
        incomplete = [(i, p) for i, p in enumerate(self.pieces) if not p.is_complete()]
        return random.choice(incomplete)
