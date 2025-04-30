import random


class Tracker:
    # Static vars
    peer_timeout = 0

    # Public Functions
    def __init__(self, address):
        self.torrents = {} # key: info_hash, val: list of peer addresses
        self.address = address
        self.actions = []

    def announce(self, info_hash, peer_address):
        # If new hash, add to torrents
        if info_hash not in self.torrents:
            self.torrents[info_hash] = []

        # Add peer if not already known
        if peer_address not in self.torrents[info_hash]:
            self.torrents[info_hash].append(peer_address)

        # return list of peers (excluding announcing peer)
        peers = [peer for peer in self.torrents[info_hash] if peer != peer_address]
        random.shuffle(peers)
        return peers

    def draw_schema(self):
        print("tracker", self.address)

        print("\t" + "tracking:")
        for ih in self.torrents.keys():
            print("\t\t" + f"{ih[:5]}..." + ": " + str(self.torrents[ih]))

        print("\t" + "actions:")
        for act in self.actions:
            print("\t\t" + act)
        self.actions.clear()