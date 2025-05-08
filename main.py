########################## Libs ##########################
import random

# Custom
from peer import Peer
from tracker import Tracker
from torrent_file import TorrentFile
import global_vars


########################## Global Vars ##########################
# Settings
PEER_AMOUNT = 3
TRACKER_AMOUNT = 1
FILE_AMOUNT = 3
FILE_SIZE_RANGE = (12, 24)
PIECE_SIZES = (4,)
BLOCK_SIZE = 1
RUN_TIME = 100
REANOUNCE_TIME = 2
PEER_TIMEOUT = 3
PEER_REQUEST_CHANCE = 0.5
RANDOM_PIECES = 1
ENDGAME_PIECES = 1
AMOUNT_UNCHOKED_PEERS = 1 # Without optimistic unchoked one
OPTIMISTIC_UNCHOKE_TIME = 2
SEED = 42

# Other
run_to_completion = False


########################## Functions ##########################
########################## Setup ##########################
def setup():
    random.seed(SEED)

    peers = {}  # key: address, val: peer object
    trackers = {}  # key: address, val: tracker object
    torrent_files = []
    global_vars.block_size = BLOCK_SIZE
    global_vars.random_pieces = RANDOM_PIECES
    global_vars.endgame_pieces = ENDGAME_PIECES
    global_vars.amount_unchoked_peers = AMOUNT_UNCHOKED_PEERS
    global_vars.optimistic_unchoke_time = OPTIMISTIC_UNCHOKE_TIME

    # Static vars
    Peer.reannounce_time = REANOUNCE_TIME
    Peer.request_chance = PEER_REQUEST_CHANCE
    Tracker.peer_timeout = PEER_TIMEOUT

    # Instantiate peers
    for i in range(PEER_AMOUNT):
        address = f"1.1.1.{i+1}:6881" # 6881 standard torrent port (old)
        peer = Peer(address)
        peers[address] = peer

    # Instantiate trackers
    for i in range(TRACKER_AMOUNT):
        address = f"1.1.1.{PEER_AMOUNT+i+1}:6881"
        tracker = Tracker(address)
        trackers[address] = tracker

    # Instantiate torrent files
    for i in range(FILE_AMOUNT):
        name = f"file_{i+1}"
        size = random.randint(FILE_SIZE_RANGE[0], FILE_SIZE_RANGE[1])

        # Torrent file
        random_tracker_address = random.choice(list(trackers.keys()))
        piece_size = random.choice(PIECE_SIZES)
        torrent_file = TorrentFile(name, size, piece_size, random_tracker_address)
        torrent_files.append(torrent_file)

        # Add files to their initial peer
        peer = random.choice(list(peers.values()))
        peer.add_file(torrent_file)


    # Export global vars
    global_vars.peers = peers
    global_vars.trackers = trackers
    global_vars.torrent_files = torrent_files


########################## Other ##########################
def draw_starttime():
    print(f"########################## time: 0 ##########################")
    for peer in global_vars.peers.values():
        peer.draw_schema()
    for tracker in global_vars.trackers.values():
        tracker.draw_schema()
    print(f"############################################################")


def handle_input():
    global run_to_completion

    if not run_to_completion:
        command = input("Press Enter:")
        if command == "r":
            run_to_completion = True


########################## Main Loop ##########################
def main_loop():
    global run_to_completion

    draw_starttime()
    handle_input()
    print("\n")
    time = 1

    while time <= RUN_TIME:
        print(f"########################## time: {time} ##########################")
        for peer in global_vars.peers.values():
            peer.execute(time)
        for tracker in global_vars.trackers.values():
            tracker.draw_schema()
        print(f"###########################################################" + "#" * (len(str(time))))

        handle_input()
        print("\n")
        time += 1


def main():
    setup()
    main_loop()


if __name__ == '__main__':
    main()

