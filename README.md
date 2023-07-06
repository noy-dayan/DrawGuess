
<p align='center'>
  <img src= 'https://user-images.githubusercontent.com/106970874/250997584-592d28e2-ce11-49fd-bea3-036df138f025.png'/>
</p>

DrawGuess is a online multiplayer video game that combines creativity and fun. 
In DrawGuess, players are given a word or phrase to draw within a limited time frame. As the artist, your task is to create a visual representation of the given word using a variety of drawing tools and colors. Meanwhile, other players in the game must guess the word based on your drawing. 

## Features

- intuitive and user-friendly interface
- Intuitive drawing tools and colors for creating visual representations.
- Real-time synchronization for seamless multiplayer gameplay.
- Lobby system for creating and joining game rooms.
- Chat functionality for players to interact and socialize.
- Point system for rewarding successful guesses and recognized drawings.

## Technologies and Modules Used

- Front-end & Back-end: Python
- Main Modules: pygame, socket, open-cv, threading and pickle

## Code Architecture
The product consists of the following main code files:
- **[server.py](server.py)**
   - Responsible for routing the information between the clients.
   - Acts as the central hub for communication within the system.

- **[menu.py](menu.py)**
   - Provides a standalone main menu interface for clients.
   - Does not require a connection to the main server.

- **[game.py](game.py)**
   - Includes the lobby hub interface and the in-game interface itself.
   - Establishes a connection to the main server for real-time interactions.

In addition to these files, there are 2 additional files with specialized roles:
- **[assets_loader.py](assets_loader.py)**
   - Loads the game screen, along with images, sounds, and various objects.

- **[classes.py](classes.py)**
   - Contains classes used by the main files.
   - Enhances code organization and reusability.

## Contact
If you have any questions, suggestions, or feedback, please feel free to contact me:
[@noy-dayan](https://www.github.com/noy-dayan)
