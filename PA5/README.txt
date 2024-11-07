# README for PA5 #
Class: Tölvugrafík 
Students:
    Ágúst Máni Þorsteinsson
    Hermann Helgi Þrastarsson

# QUASAR TAG #
This is the submission for Project Assignment 5 for for the class Computer Graphics in HR.
Our submission holds the name of Quasar Tag, a Free-for-all FPS PVP game with LAN multiplayer. 
Players who join the server will be thrust into a small arena where the goal is to be the last one standing.
Players can shoot at each other with lasers, which pierce through all objects and cover!

# HOW TO RUN #
To run this submission, the user will have to have pre-installed the given python libraries:

    pip install Numpy
    pip install Pygame
    pip install PyOpenGl.

Once the libraries are installed, the next step is to run the main server.py file. It will request a port number
for its networking uses once initiated. Any port number which is open should be fine.

    py ./server.py

    # INPUT: 
    Please provide a port to host on: <PORT>

Once the server is running, it should allow any player on the LAN to join. 
We cannot promise that a host can join from a separate network as we have not tested it. 
Such a connection might require port forwarding on the hosts side.

IMPORTANT NOTE: Due to the multithreading required, the server cannot be closed without force. 
Killing the terminal for the server will shut it down, but it will remain if not forcibly closed.

Running the Game.py file will initiate a client. On start, the user will be prompted for the IP address of the host,
as well as their port number. If the server is on the same device as the client, entering nothing into the IP address
will connect the client to the localhost, a port number is still required.

    py ./Game.py

    # INPUT:
    Please provide an ip to connect to (leave blank for localhost): <HOST IP>
    Please provide a port: <HOST PORT>

The connection should then be made, and the client will join the server.

# CONTROLS #
The player can move and look around the game scene with the controls:

    WASD for movement.
    Shift can be used to run.
    Mouse pad or mouse movement to look around.

The player can fire a laser which pierces all walls to shoot other players.

    Left click to shoot.

Once the player has run out of lives, indicated by the 0 in the top right corner, they become a spectator.
A spectator can move around with all the same movements keys as a player, except they can fly and can go through objects.
A player can respawn with the given button:

    Spacebar to respawn.

The camera of the player can dictate how fast the player moves. 
If looked directly down/up the player will become frozen in place.