# All these vars are assumed to be globally accessible

peers = {}  # key: address, val: peer object
trackers = {}  # key: address, val: tracker object
torrent_files = []
block_size = 0
random_pieces = 0
endgame_pieces = 0
amount_unchoked_peers = 0
optimistic_unchoke_time = 0