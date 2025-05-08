# BDA_Project
## How it works
This program simulates peers using the BitTorrent protocol. It does not send actual files over a network, or use multiple threads, however the algorithms are implemented accurately.
The piece selection algorithm is implemented, with random-first, rarest-first, and endgame-mode strategies. The peers are also required to use the strict-priority policy.
Furthermore, the tit-for-tat policy is implemented with the unchoking algorithm, also taking care of optimistic unchoking of random peers.
Even though this is a simulation, it is as close to realistic as possible. The peers and trackers are stored by their address to simulate searching them over the internet.
The information of a file is all stored in a torrent-file, which here is not a typical file, but a class containing information, like, info, info-hash, announce....
The files are also searched for by the peers on the basis of their bencoded info-hash, like in actual BitTorrent (also done with sha1).

When running *main.py*, the program starts at time 0, with a set amount of files, peers and trackers. The files are instantiated with a random size, and piece size. (All settings can be changed in *main.py*.)
Upon running, click *ENTER* in the console to increment the time by 1, type *r* to run to completion. The peers will, from time to time, request a random file, by accessing the torrent file and calling a tracker.
All decisions made, and the working of the algorithms, can be checked by the printed output in the console.

## Technical details
The working of the files in this project are explained below:
* **choke_information:** Contains, and calculates the upload_rate necessary for unchoking.
* **file_information:** Since no actual files are used, this contains a class that keeps track of the files' properties.
* **global_vars:** A collection of global variables.
* **main:** The file needed to setup everything and run the simulation.
* **peer:** This contains the class Peer, which handles the logic a peer handles in BitTorrent: Piece selection, Downloading, Unchoking, Connecting...
* **piece:** A class storing the blocks a certain piece has.
* **torrent_file:** For storing information about a file.
* **tracker**: This handles the tracker logic, like in actual BitTorrent.


This project is run with Python 3.9, requirements can be found in *requirements.txt*.
