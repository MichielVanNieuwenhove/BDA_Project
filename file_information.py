
class FileInformation:
    def __init__(self, torrent_file, amount_pieces, empty=True):
        self.pieces = [int(not empty)] * amount_pieces
        self.last_announce = -100
        self.torrent_file = torrent_file

