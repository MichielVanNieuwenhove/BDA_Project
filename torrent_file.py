import hashlib
import bencodepy
import math


class TorrentFile:
    def __init__(self, name, size, piece_size, tracker_address):
        self.info = {
            "name": name,
            "piece_length": piece_size,
            "length": size
        } # A lot of fields left out, not necessary in this simulation
        self.announce = tracker_address
        self.info_hash = self.__create_info_hash__()
        self.amount_pieces = math.ceil(size / piece_size)

    def __create_info_hash__(self):
        bencoded_info = bencodepy.encode(self.info)
        return hashlib.sha1(bencoded_info).hexdigest()
