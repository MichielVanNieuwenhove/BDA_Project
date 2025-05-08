import global_vars
from file_information import FileInformation
import random
from enum import Enum
import numpy as np
from choke_information import ChokeInformation


class Peer:
    ########################## Static vars ##########################
    reannounce_time = 0
    request_chance = 0


    ########################## Constructor ##########################
    def __init__(self, address):
        self.address = address
        self.files = {} # key: info hash, val: file information object
        self.actions = []
        self.requesting_hash = ""
        self.requesting_piece_idx = -1
        self.requesting_piece = None
        self.connected_peers_seeders = []
        self.connected_peers_leechers = []
        self.choke_information_list = {}
        self.unchoked_peers = []
        self.last_optimistic_unchoke = -100
        self.download_strategy = DownloadStrategy.RANDOM_FIRST


    ########################## Public functions ##########################
    def execute(self, time):
        self.__announce__(time)

        # Unchoke top k peers
        for peer in list(self.choke_information_list.keys()):
            if peer not in self.connected_peers_seeders:
                self.choke_information_list.pop(peer)

        for peer in self.connected_peers_seeders:
            if peer not in self.choke_information_list.keys():
                self.choke_information_list[peer] = ChokeInformation()
            self.choke_information_list[peer].add_upload(time)

        sorted_peers = sorted(
            self.choke_information_list.items(),
            key=lambda item: item[1].upload_rate,
            reverse=True
        )
        self.unchoked_peers = [peer for peer, _ in sorted_peers[:global_vars.amount_unchoked_peers]]

        # Fill remaining slots with random peers if needed
        if len(self.unchoked_peers) < global_vars.amount_unchoked_peers:
            remaining_candidates = [peer for peer in self.connected_peers_leechers
                                    if peer not in self.unchoked_peers]
            needed = global_vars.amount_unchoked_peers - len(self.unchoked_peers)
            random.shuffle(remaining_candidates)
            self.unchoked_peers.extend(remaining_candidates[:needed])

        # Handle optimistic unchoking
        if time - self.last_optimistic_unchoke >= global_vars.optimistic_unchoke_time:
            self.last_optimistic_unchoke = time
            remaining_peers = [peer for peer in self.connected_peers_leechers if peer not in self.unchoked_peers]
            if remaining_peers:  # Make sure the list is not empty
                optimistic_peer = random.choice(remaining_peers)
                self.actions.append(f"optimistically unchoked {optimistic_peer.address}")
                self.unchoked_peers.append(optimistic_peer)

        # New requests
        if self.requesting_hash == "":
            new_request_bool = random.random()
            if new_request_bool < self.request_chance:
                self.__request_random_file__()

        # Download pieces
        else:
            requesting_file = self.files[self.requesting_hash]
            seeders_pieces_mask = [peer.get_pieces_mask(self.requesting_hash) for peer in self.connected_peers_seeders]

            # Check if current piece is complete (or if there even is a current piece)
            new_piece = True
            if self.requesting_piece is not None:
                if not self.requesting_piece.is_complete():
                    new_piece = False

            # If new piece necessary implement download strategy to get it.
            if new_piece:
                if self.download_strategy == DownloadStrategy.RANDOM_FIRST:
                    self.requesting_piece_idx, self.requesting_piece = requesting_file.get_random_incomplete_piece()
                else: # Rarest first (Endgame also uses rarest first)
                    mask = np.array(seeders_pieces_mask)
                    piece_availability = mask.sum(axis=0)
                    incomplete_indexes = [i for i, p in enumerate(requesting_file.pieces) if not p.is_complete()]
                    available_incomplete = [(i, piece_availability[i]) for i in incomplete_indexes if
                                            piece_availability[i] > 0]

                    min_rarity = min(count for _, count in available_incomplete)
                    rarest_pieces = [i for i, count in available_incomplete if count == min_rarity]
                    self.requesting_piece_idx = random.choice(rarest_pieces)
                    self.requesting_piece = requesting_file.pieces[self.requesting_piece_idx]

            # Get seeders with this piece
            seeders_with_piece = [
                peer for peer, mask in zip(self.connected_peers_seeders, seeders_pieces_mask)
                if mask[self.requesting_piece_idx]
            ]

            # Download blocks from the current piece
            if self.download_strategy == DownloadStrategy.ENDGAME_MODE:
                block_idx = self.requesting_piece.get_first_incomplete_idx()
                is_downloaded = False
                for seeder_idx in range(len(seeders_with_piece)):
                    can_download = self.connected_peers_seeders[seeder_idx].download(self)
                    if can_download:
                        is_downloaded = True
                        self.actions.append(f"Downloading block {block_idx}, for piece {self.requesting_piece_idx}, "
                                            f"of file {self.requesting_hash[:5]}..., "
                                            f"from peer {seeders_with_piece[seeder_idx].address}")
                if is_downloaded:
                    self.requesting_piece.set_block(block_idx)
            else:
                first_incomplete_block_idx = self.requesting_piece.get_first_incomplete_idx()
                amount_incomplete_blocks = self.requesting_piece.amount_blocks - first_incomplete_block_idx
                seeder_idx = 0
                for i in range(min(amount_incomplete_blocks, len(seeders_with_piece))):
                    can_download = self.connected_peers_seeders[seeder_idx].download(self)
                    if can_download:
                        block_idx = i + first_incomplete_block_idx

                        self.requesting_piece.set_block(block_idx)
                        self.actions.append(f"Downloading block {block_idx}, for piece {self.requesting_piece_idx}, "
                                            f"of file {self.requesting_hash[:5]}..., "
                                            f"from peer {seeders_with_piece[seeder_idx].address}")
                    seeder_idx += 1

            # Stop download, or change strategy (count amount incomplete)
            incomplete_count = 0
            for piece in requesting_file.pieces:
                if not piece.is_complete():
                    incomplete_count += 1

            if incomplete_count == 0:
                self.__stop_download__()
            elif (requesting_file.torrent_file.amount_pieces - incomplete_count) >= global_vars.random_pieces:
                self.download_strategy = DownloadStrategy.RAREST_FIRST
                self.actions.append("Strategy set to RAREST FIRST")
            if incomplete_count <= global_vars.endgame_pieces:
                self.download_strategy = DownloadStrategy.ENDGAME_MODE
                self.actions.append("Strategy set to ENDGAME MODE")

        self.draw_schema()

    def add_file(self, torrent_file, empty=False):
        file_information = FileInformation(torrent_file, torrent_file.amount_pieces, empty=empty)
        self.files[torrent_file.info_hash] = file_information

    def draw_schema(self):
        print("peer:", self.address)

        print("\t" + "files:")
        for fi in self.files.values():
            print("\t\t" + fi.torrent_file.info["name"] + ": " +
                  f"{fi.torrent_file.info_hash[:5]}..." + " | " +
                  f"size: {fi.torrent_file.info['length']}" + " | " +
                  f"piece size: {fi.torrent_file.info['piece_length']}" + " | " +
                  "pieces: " + str([str(piece.blocks) for piece in fi.pieces]))

        print("\t" + "actions:")
        for act in self.actions:
            print("\t\t" + act)
        self.actions.clear()

        print("\t" + f"requesting file: {self.requesting_hash[:5]}..., piece idx: {self.requesting_piece_idx}, strategy: {self.download_strategy}")

        seeders_addresses = [peer.address for peer in self.connected_peers_seeders]
        leechers_addresses = [peer.address for peer in self.connected_peers_leechers]
        print("\t" + f"connected peers: {str(set(seeders_addresses + leechers_addresses))}")

        print("\t" + f"unchoked peers: {[str(peer.address) for peer in self.unchoked_peers]}")

    def connect(self, peer, file_hash):
        self.connected_peers_leechers.append(peer)
        self.actions.append(f"Connect to {peer.address} for seeding file {file_hash[:5]}...")

    def disconnect(self, peer):
        self.connected_peers_leechers.remove(peer)
        self.actions.append(f"Disconnect from {peer.address} after seeding")

    def get_pieces_mask(self, file_hash):
        return [piece.is_complete() for piece in self.files[file_hash].pieces]

    def download(self, peer):
        if peer in self.unchoked_peers:
            return True
        else:
            return False

    ########################## Private functions ##########################
    def __announce__(self, time):
        # Loop through files and announce if time passed
        for fi in self.files.values():
            if time - fi.last_announce >= self.reannounce_time:
                # Announce & connect to seeders
                tracker_address = fi.torrent_file.announce
                tracker = global_vars.trackers[tracker_address]
                peers_addresses = tracker.announce(fi.torrent_file.info_hash, self.address)
                if (fi.torrent_file.info_hash == self.requesting_hash) and (not self.connected_peers_seeders):
                    self.connected_peers_seeders = [global_vars.peers[address] for address in peers_addresses]
                    for peer in self.connected_peers_seeders:
                        self.__connect_to__(peer)

                # Reset timer
                fi.last_announce = time

                # Add action
                self.actions.append(f"Announced file: {fi.torrent_file.info_hash[:5]}..., to tracker: {tracker_address}")

    def __connect_to__(self, peer):
        peer.connect(self, self.requesting_hash)
        self.actions.append(f"Connect to {peer.address} for leeching file {self.requesting_hash[:5]}...")

    def __request_random_file__(self):
        filtered_files = [file for file in global_vars.torrent_files if file.info_hash not in self.files.keys()]
        if filtered_files:
            tf = random.choice(filtered_files)
            self.add_file(tf, empty=True)
            self.requesting_hash = tf.info_hash

    def __stop_download__(self):
        self.requesting_hash = ""
        self.download_strategy = DownloadStrategy.RAREST_FIRST
        self.requesting_piece = None
        self.requesting_piece_idx = -1
        for peer in self.connected_peers_seeders:
            peer.disconnect(self)
            self.actions.append(f"Disconnect from {peer.address} after leeching")
        self.connected_peers_seeders.clear()



class DownloadStrategy(Enum):
    RANDOM_FIRST = 1
    RAREST_FIRST = 2
    ENDGAME_MODE = 3