#!/usr/bin/python3.7.4
# Setup Python ----------------------------------------------- #
import socket
from threading import Thread
from classes import Client, Lobby, Pen
import pickle
from random import sample

# Setup Server ----------------------------------------------- #
class Server(object):
    # Constructor ------------------------------------------------ #
    def __init__(self, IP, PORT):
        # Creates the main server. Receives IP and PORT.
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (IP, PORT)
        self.server.bind(self.addr)
        self.clients = []
        self.threads = []
        self.active_conns = 0
        self.lobby_list = []
        self.lobby_count = 0

    # Server management ------------------------------------------ #
    def server_management(self):
        # The main function of the department - manages the client connection at the same time.
        # data reset
        for client in self.clients:
            client.close()
        del self.clients[:]
        # server management
        # client connection
        while True:
            client, addr = self.server.accept()
            c1 = Client(client, addr)
            self.clients.append(c1)
            c1.setIndex(self.clients.index(c1))
            self.send(c1, ['NICK', c1.getClientID()], 2)
            nickname = self.recv(c1)
            self.clients[c1.getIndex()].setNickname(nickname)
            self.active_conns += 1

            print(
                f"[NEW CONNECTION] Address: [{str(addr[0])}:{str(addr[1])}] |"
                f" Nickname: {self.clients[c1.getIndex()].getNickname()} | "
                f"Active Connections: {self.active_conns}")

            # thread management
            t = Thread(target=self.handle_client, args=(c1,))
            t.start()
            self.threads.append(t)

    # Data handler functions ------------------------------------- #
    def send(self, c1, data, to=0 or 1 or 2):
        # Send information to clients.
        """
        to = 0 -> send to every client in the lobby
        to = 1 -> send to every client in the lobby except c1
        to = 2 -> send to c1
        """
        try:
            try:
                for client in self.clients:
                    if c1 == client:
                        c1.setIndex(self.clients.index(client))
                for lobby in self.lobby_list:
                    if c1 in lobby.getPlayersList():
                        c1.setLobby(self.lobby_list.index(lobby) + 1)
            except Exception as e:
                print(e)
            if to == 0:
                for client in self.lobby_list[c1.getLobby() - 1].getPlayersList():
                    if client is not None:
                        client.getClient().sendall(pickle.dumps(data))
            elif to == 1:
                for client in self.lobby_list[c1.getLobby() - 1].getPlayersList():
                    if client != c1 and client is not None:
                        client.getClient().sendall(pickle.dumps(data))
            elif to == 2:
                c1.getClient().sendall(pickle.dumps(data))
        except Exception as e:
            print(f"[ERROR] An error occurred while trying to 'send':\n{e}")

    @staticmethod
    def recv(c1):
        # Receive information from clients and apply accordingly.
        try:
            try:
                return pickle.loads(c1.getClient().recv(1024 * 2))
            except:
                pass
        except Exception as e:
            print(f"[ERROR] An error occurred while trying to 'recieve':\n{e}")

    # Client handler --------------------------------------------- #
    def server_cmd_dict(self):
        # A dictionary containing all the commands that can be requested by clients.
        return {'CHAT_MSG': self.cmd_chatMsg,
                'DO_FILL': self.cmd_doFill,
                'COUNTDOWN': self.cmd_countdown,
                'SCORE': self.cmd_score,
                'ROUND_OVER': self.cmd_roundOver,
                'CREATE_LOBBY': self.cmd_createLobby,
                'JOIN_LOBBY': self.cmd_joinLobby,
                'LOBBIES_SPECS': self.cmd_lobbySpecs,
                'START_GAME': self.cmd_startGame,
                'DRAW': self.cmd_draw,
                'DO_CLEAR': self.cmd_doClear,
                'ANNOUNCE_WINNER': self.cmd_announceWinner}

    def cmd_announceWinner(self, c1):
        # Sends the winner to all clients and restarts the game.
        if c1 == self.lobby_list[c1.getLobby()-1].getPlayersList()[0]:
            winner = None
            nick_list = self.getPlayersList(c1)
            del nick_list[0]
            for player in nick_list:
                if winner is None:
                    winner = player
                else:
                    if int(winner[1]) < int(player[1]):
                        winner = player
            self.send(c1, ['ANNOUNCE_WINNER', winner[0]], 0)
            self.lobby_list[c1.getLobby()-1].setWords(Lobby.getRandomWord(6))
            self.send(c1, ['WORDS', self.lobby_list[c1.getLobby()-1].getWords()], 0)
            self.lobby_list[c1.getLobby()-1].setGameStatus('INACTIVE')
            for client in self.clients:
                if client.getClientStatus() == 'In_Lobby_Picker':
                    self.cmd_lobbySpecs(client)

    def cmd_draw(self, c1, msg):
        # Sends the drawing details to all clients in the lobby except c1.
        self.send(c1, msg, 1)

    def cmd_doClear(self, c1):
        # Sends to all clients in the lobby except c1 the command to the board clear function.
        self.send(c1, 'DO_CLEAR', 1)

    def cmd_chatMsg(self, c1, msg):
        # Sends the chat message to all clients in the lobby.
        self.send(c1, msg, 0)

    def cmd_doFill(self, c1, msg):
        # Sends to all clients in the lobby except c1 the command to the bucket filling function.
        self.send(c1, msg, 1)

    def cmd_countdown(self, c1, msg):
        # Sends the timer to all clients in the lobby except c1.
        self.send(c1, msg, 1)

    def cmd_roundOver(self, c1, msg):
        # Sends to all clients in the lobby on the start of a new round.
        if len(self.lobby_list[c1.getLobby() - 1].getPlayersList()) > 0:
            for client in self.lobby_list[c1.getLobby() - 1].getPlayersList():
                if c1 == client:
                    client.setWasPainter(True)
                    if msg[1] is not None:
                        client.setScore(str(msg[1]))
                    break
            painter = self.getRandomPainter(c1)
            self.send(c1, ['NEXT_ROUND', painter.getClientID(), self.getPlayersList(c1), str(painter.getNickname())], 0)
            words = self.lobby_list[c1.getLobby() - 1].getWords()
            if msg[1] is None:
                words.append(Lobby.getRandomWord(1)[0])
            del words[0]
            self.send(c1, ['WORDS', words], 0)

    def cmd_createLobby(self, c1, msg):
        # Updates the list of lobbies (in a new lobby) and sends the client the details of the game.
        self.lobby_list.append(Lobby(c1, msg[1], msg[2]))
        self.lobby_count += 1
        c1.setLobby(self.lobby_count)
        c1.setClientStatus('In_Game')
        print(f"[NEW LOBBY] A new lobby has been formed | "
              f"Lobby {c1.getLobby()} | "
              f"Owner: {c1.getNickname()}")
        self.send(c1, ['GAME_PREP', self.getPlayersList(c1),
                       self.lobby_list[c1.getLobby() - 1].getWords(),
                       self.lobby_list[c1.getLobby()-1].getLobbyOwner().getClientID()], 0)
        for client in self.clients:
            if client.getClientStatus() == 'In_Lobby_Picker':
                self.cmd_lobbySpecs(client)

    def cmd_joinLobby(self, c1, msg):
        # Updates the list of lobbies (in a new player) and sends the client the details of the game.
        for lobby in self.lobby_list:
            if lobby.getGameStatus() == 'INACTIVE' and len(lobby.getPlayersList()) < 6:
                if msg[1] == lobby.getLobbySpecs()[0] and msg[2] == lobby.getLobbySpecs()[1]:
                    c1.setLobby(self.lobby_list.index(lobby)+1)
                    c1.setClientStatus('In_Game')
                    self.lobby_list[c1.getLobby() - 1].appendPlayersList(c1)
                    self.send(c1, ['GAME_PREP', self.getPlayersList(c1),
                                   self.lobby_list[c1.getLobby() - 1].getWords(),
                                   self.lobby_list[c1.getLobby()-1].getLobbyOwner().getClientID()], 0)
        for client in self.clients:
            if client.getClientStatus() == 'In_Lobby_Picker':
                self.cmd_lobbySpecs(client)

    def cmd_lobbySpecs(self, c1):
        # Sends to c1 the list of lobbies.
        self.send(c1, self.getLobbyListSpecs(), 2)

    def cmd_startGame(self, c1):
        # Sends to all players in the lobby that the game starts in addition to more details about the game.
        painter = self.getRandomPainter(c1)
        self.send(c1, ['START_GAME', painter.getClientID(), str(painter.getNickname())], 0)
        self.lobby_list[c1.getLobby()-1].setGameStatus('ACTIVE')
        for client in self.clients:
            if client.getClientStatus() == 'In_Lobby_Picker':
                self.cmd_lobbySpecs(client)

    @staticmethod
    def cmd_score(c1, msg):
        # Determines the score of c1.
        c1.setScore(str(msg[1]))

    def handle_client(self, c1):
        # After routing the information from the client to the appropriate commands.
        while True:
            for client in self.clients:
                if c1 == client:
                    c1.setIndex(self.clients.index(client))
            for lobby in self.lobby_list:
                if c1 in lobby.getPlayersList():
                    c1.setLobby(self.lobby_list.index(lobby) + 1)
            msg = self.recv(c1)
            if type(msg) is Pen:
                self.send(c1, msg, 1)
            else:
                if type(msg) is list:
                    info = msg[0]
                    if info in self.server_cmd_dict().keys():
                        self.server_cmd_dict()[info](c1, msg)

                elif type(msg) is str:
                    if msg in self.server_cmd_dict().keys():
                        self.server_cmd_dict()[msg](c1)

                    elif 'DISCONNECT' == msg:
                        break

        self.quit_progress(c1)

    # Getters ---------------------------------------------------- #
    def getPlayersList(self, c1):
        nick_list = ['NICKNAME_LIST']
        if self.lobby_count > 0:
            for client in self.lobby_list[c1.getLobby() - 1].getPlayersList():
                nick_list.append((client.getNickname(), client.getScore()))
        return nick_list

    def getLobbyListSpecs(self):
        lobby_list_specs = ['LOBBIES_SPECS']
        for lobby in self.lobby_list:
            if lobby.getLobbySpecs()[1] is None:
                locked = False
            else:
                locked = True
            lobby_list_specs.append([lobby.getLobbySpecs()[0], str(lobby.getLobbyOwner()),
                                     len(lobby.getPlayersList()), locked, lobby.getGameStatus()])
        return lobby_list_specs

    def getRandomPainter(self, c1):
        approved_clients = []
        self.append_approved_clients(c1, approved_clients)
        if len(approved_clients) == 0:
            self.reset_client_approval(c1)
            self.append_approved_clients(c1, approved_clients)
        return sample(approved_clients, 1)[0]

    def reset_client_approval(self, c1):
        # Initializes the list of valid actors to be painters.
        for client in self.lobby_list[c1.getLobby() - 1].getPlayersList():
            if c1 != client:
                client.setWasPainter(False)

    def append_approved_clients(self, c1, approved_clients):
        # Expands the list of valid actors to become painters.
        for client in self.lobby_list[c1.getLobby() - 1].getPlayersList():
            if not client.getWasPainter():
                approved_clients.append(client)

    # Connection handler functions ------------------------------- #
    def quit_progress(self, c1):
        # The process of disconnecting the client from the server.
        # If the lobby were empty, the lobby would be deleted and removed from the system.
        if self.active_conns > 0:
            self.active_conns -= 1
        for lobby in self.lobby_list:
            if c1 in lobby.getPlayersList():
                c1.setLobby(self.lobby_list.index(lobby) + 1)
        for client in self.clients:
            if c1 == client:
                c1.setIndex(self.clients.index(client))
        print(
            f"[DISCONNECTION]  Address: [{c1.getAddr()[0]}:{str(c1.getAddr()[1])}]"
            f" | Nickname: {c1.getNickname()} | Lobby: {c1.getLobby()} | Active Connections: {self.active_conns}")
        if self.lobby_count > 0 and c1.getLobby() is not None:
            self.lobby_list[c1.getLobby() - 1].removePlayersList(c1)
            if len(self.lobby_list[c1.getLobby()-1].getPlayersList()) > 0:
                self.send(c1, self.getPlayersList(c1), 1)
                if c1 == self.lobby_list[c1.getLobby()-1].getLobbyOwner():
                    self.lobby_list[c1.getLobby() - 1].setLobbyOwner(self.lobby_list[c1.getLobby()-1].getPlayersList()[0])
                    self.send(c1, ['SET_OWNER_ID', self.lobby_list[c1.getLobby() - 1].getLobbyOwner().getClientID()], 1)
            if len(self.lobby_list[c1.getLobby() - 1].getPlayersList()) == 0:
                del self.lobby_list[c1.getLobby() - 1]
                self.lobby_count -= 1
                print(f"[LOBBY REMOVAL] Lobby has been deconstructed | Lobby {c1.getLobby()} "
                      f"| Remaining Lobbies: {self.lobby_count}")
        del self.clients[c1.getIndex()]
        del self.threads[c1.getIndex()]
        c1.close()
        for client in self.clients:
            if client.getClientStatus() == 'In_Lobby_Picker':
                self.cmd_lobbySpecs(client)

    def listen(self):
        # A function whose function is to listen to a request for connection from the client.
        self.server.listen()

    def close(self):
        # A function that closes the server.
        self.server.close()

# main function -------------------------------------------------- #
def main():
    IP = '127.0.0.1'
    PORT = 5055
    server = Server(IP, PORT)
    server.listen()
    print("_____________________________________________\n"
          "[STARTING]  Server has been established...\n"
          f"[LISTENING] Server is listening on {IP}\n"
          "_____________________________________________\n")
    server.server_management()
    server.close()


if __name__ == '__main__':
    main()
