import global_vars
from file_information import FileInformation
import random


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
        self.connected_peers_seeders = []
        self.connected_peers_leechers = []


    ########################## Public functions ##########################
    def execute(self, time):
        self.__announce__(time)

        # New requests
        if self.requesting_hash == "":
            new_request_bool = random.random()
            if new_request_bool < self.request_chance:
                self.__request_random_file__()

        # Download pieces
        elif 0 in self.files[self.requesting_hash].pieces: # Check to stop downloading
            position_counts = self.__get_position_counts__()

            # Don't download a piece you already have, even if it is the rarest still
            max_count = max(position_counts)
            for i, val in enumerate(self.files[self.requesting_hash].pieces):
                if val == 1:
                    position_counts[i] = max_count + 1

            # Sort on rarest first
            rarest_positions = sorted(range(len(position_counts)), key=lambda i: position_counts[i])

            # Download pieces in ascending rarity
            used_peers = set()
            for rp in rarest_positions:
                for peer in self.connected_peers_seeders:
                    if peer not in used_peers and peer.files[self.requesting_hash].pieces[rp]:
                        self.files[self.requesting_hash].pieces[rp] = 1
                        self.actions.append(f"Downloaded piece {rp} for file {self.requesting_hash[:5]}... from {peer.address}")
                        used_peers.add(peer)
                        break

        # Stop download
        else:
            self.__stop_download__()

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
                  str(fi.pieces))

        print("\t" + "actions:")
        for act in self.actions:
            print("\t\t" + act)
        self.actions.clear()

        print("\t" + f"requesting file: {self.requesting_hash[:5]}...")

        seeders_addresses = [peer.address for peer in self.connected_peers_seeders]
        leechers_addresses = [peer.address for peer in self.connected_peers_leechers]
        print("\t" + f"connected peers: {str(set(seeders_addresses + leechers_addresses))}")

    def connect(self, peer, file_hash):
        self.connected_peers_leechers.append(peer)
        self.actions.append(f"Connect to {peer.address} for seeding file {file_hash[:5]}...")

    def disconnect(self, peer):
        self.connected_peers_leechers.remove(peer)
        self.actions.append(f"Disconnect from {peer.address} after seeding")


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
        for peer in self.connected_peers_seeders:
            peer.disconnect(self)
            self.actions.append(f"Disconnect from {peer.address} after leeching")
        self.connected_peers_seeders.clear()

    def __get_position_counts__(self):
        # Count for every connected seeder combined the amount of every piece there is
        position_counts = [0] * len(self.files[self.requesting_hash].pieces)
        for peer in self.connected_peers_seeders:
            pieces = peer.files[self.requesting_hash].pieces
            for i, piece in enumerate(pieces):
                position_counts[i] += piece

        return position_counts