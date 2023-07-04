#!/usr/bin/python3.7.4
# Setup Python ----------------------------------------------- #
from assets_loader import *
from classes import Player
from threading import Thread
import socket
import pickle
import sys
import time


# Setup Pygame/game ------------------------------------------ #
class Game:
    # Constructor ------------------------------------------------ #
    def __init__(self, screen, music, nickname=None):
        # Creates the user interface with connection to the server and displays the lobby inlay menu and the game itself.
        self.screen = screen
        self.music = music
        if nickname is not None:
            self.player = Player(nickname)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_id = ''
        self.connected = False
        self.active_conns = 0
        self.thread = None

        self.lobby_specs = ['', None]  # [Lobby name, Lobby password]
        self.lobby_filters = [False, False]  # [Hide full lobbies, Hide locked lobbies]
        self.lobby_picker_arrows_pos = 0
        self.lobby_list = []
        self.lobby_owner_id = ''

        self.pen = Pen()
        self.nick_list = []
        self.chat_list = []
        self.rounds_left = 0
        self.game_page = 'In_Lobby_Picker'
        self.winner = None

        self.counter = 60
        self.words = []
        self.painter = ''

        self.pos = (0, 0)
        self.rel = (0, 0)
        self.board_x = 415 * self.screen.getWidthScale(), 1420 * self.screen.getWidthScale()
        self.board_y = 100 * self.screen.getHeightScale(), 925 * self.screen.getHeightScale()

    # Getters ---------------------------------------------------- #
    def getUniversalPos(self, pos):
        return int(round(pos[0] * 1920) / self.screen.getWidth()), int(round(pos[1] * 1080) / self.screen.getHeight())

    def getUniquePos(self, pos):
        return int(pos[0] * self.screen.getWidthScale()), int(pos[1] * self.screen.getHeightScale())

    # Setters ---------------------------------------------------- #
    def setPlayer(self, nickname):
        self.player = Player(nickname)

    # Server connection functions -------------------------------- #
    def send(self, data):
        # Send information to the main server.
        try:
            try:
                msg = pickle.dumps(data)
                self.client.sendall(msg)
            except Exception as e:
                if self.connected:
                    print(f"[ERROR] An error occurred while trying to 'send':\n{e}")
                    if str(e) == '[WinError 10054] An existing connection was forcibly closed by the remote host':
                        self.connected = False
                        self.client.close()
                        self.screen.update()
        except:
            pass

    def recv(self):
        # Receive information from the main server and apply accordingly.
        try:
            try:
                msg = pickle.loads(self.client.recv(1024))
                return msg
            except Exception as e:
                if str(e) == '[WinError 10054] An existing connection was forcibly closed by the remote host':
                    self.connected = False
                    self.client.close()
                    self.screen.update()
        except Exception as e:
            if self.connected:
                print(f"[ERROR] An error occurred while trying to 'recieve':\n{e}")

    def connect(self):
        # Try and connect to the primary server as a client.
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.connected is False:
            try:
                self.game_page = 'In_Lobby_Picker'
                lobby_name_box.setText('')
                lobby_password_box.setText('')
                self.client.connect(self.player.getAddr())
                print(f"\n_____________________________________________"
                      f"\n[CONNECTION] You have been connected to the server."
                      f"\n[NICKNAME] {self.player.getNickname()}")
                data = self.recv()
                if data[0] == 'NICK':
                    self.send(self.player.getNickname())
                    self.client_id = data[1]
                    print(f"[CLIENT-ID] {self.client_id}"
                          f"\n_____________________________________________")
                self.connected = True
            except Exception as e:
                print(f"[ERROR] Connection problem has occurred!: {e}")
                self.connected = False

    def close(self):
        # Disconnect from the main server and return to the main menu window.
        if self.player.getIsPainter() and self.rounds_left > 0 and self.active_conns > 1:
            self.send(['ROUND_OVER', None])
            time.sleep(0.2)

        self.send('DISCONNECT')
        self.client.close()

    def handle_game(self):
        # A loop that takes care of receiving the information received from the main server at any given moment
        # and according to the information to implement accordingly.
        while self.connected:
            try:
                msg = self.recv()
                if type(msg) is Pen:
                    self.pen = msg

                else:
                    if type(msg) is list:
                        info = msg.pop(0)
                        if info in self.client_cmd_dict().keys():
                            self.client_cmd_dict()[info](msg)

                    elif type(msg) is str:
                        if msg in self.client_cmd_dict().keys():
                            self.client_cmd_dict()[msg]()

            except Exception as e:
                print(e)

    # Server commands -------------------------------------------- #
    def client_cmd_dict(self):
        # A dictionary that contains all the commands that can be requested by the main server.
        return {'NICKNAME_LIST': self.cmd_nicknameList,
                'CHAT_MSG': self.cmd_chatMsg,
                'WORDS': self.cmd_words,
                'NEXT_ROUND': self.cmd_nextRound,
                'DO_FILL': self.cmd_doFill,
                'DRAW': self.cmd_draw,
                'COUNTDOWN': self.cmd_countdown,
                'IS_PAINTER': self.cmd_isPainter,
                'DO_CLEAR': self.cmd_doClear,
                'LOBBIES_SPECS': self.cmd_lobbySpecs,
                'GAME_PREP': self.cmd_gamePrep,
                'SET_OWNER_ID': self.cmd_setOwnerID,
                'START_GAME': self.cmd_startGame,
                'ANNOUNCE_WINNER': self.cmd_announceWinner}

    def cmd_announceWinner(self, msg):
        # When a request is received from the server - clears the points from all players.
        # Then, it is transferred to the end of the game stage and announces the winner (which he receives from the server)
        print(f"Winner: {msg[0]}")
        self.winner = str(msg[0])
        self.chat_list = []
        for player in self.nick_list:
            self.nick_list[self.nick_list.index(player)] = (player[0], 0)
        self.send(['SCORE', 0])
        self.game_page = 'In_End_Game'

    def cmd_setOwnerID(self, msg):
        # When a request is received from the server - updates the manager's ID card for all players
        # (which he receives from the server)
        self.lobby_owner_id = msg[0]

    def cmd_nicknameList(self, msg):
        # When a request is received from the server - updates the list of players and the number of
        # players in the lobby (which he receives from the server)
        self.nick_list = msg
        self.active_conns = len(self.nick_list)

    def cmd_chatMsg(self, msg):
        # When a request is received from the server - updates the chat message list with a new message
        # (which it receives from the server)
        msg = ' '.join(msg)
        if 'has guessed the word!          ' in msg:
            self.player.setNumOfGuessers(self.player.getNumOfGuessers() + 1)
        self.chat_list.append(msg)
        print(msg)

    def cmd_words(self, msg):
        # When a request is received from the server - updates the list of words and the number of
        # remaining rounds (which he receives from the server)
        self.words = msg[0]
        self.rounds_left = len(self.words)

    def cmd_nextRound(self, msg):
        # When a request is received from the server - updates all items regarding the next round
        # (which he receives from the server)
        global draw_on
        draw_on = False
        del msg[1][0]
        self.nick_list = msg[1]
        self.counter = 60
        self.player.setGuessed(False)
        self.player.setNumOfGuessers(0)
        del self.words[0]
        self.rounds_left = len(self.words)
        self.painter = msg[2]
        if self.client_id == msg[0]:
            self.player.setIsPainter(True)
            self.screen.getScreen().fill((255, 255, 255))
            self.screen.blit(painter_interface, (0, 0))
        else:
            self.player.setIsPainter(False)
            self.screen.getScreen().fill((255, 255, 255))
            self.screen.blit(guesser_interface, (0, 0))

    def cmd_doFill(self, msg):
        # When a request is received from the server - performs the fill bucket function
        # for all players except the painter.
        self.pen.flood_fill(self.screen, self.getUniquePos(msg[0]))

    def cmd_draw(self, msg):
        # When a request is received from the server - performs the pen function for all players except the painter.
        pg.draw.circle(self.screen.getScreen(), self.pen.getColor(), self.getUniquePos(msg[0]),
                       self.pen.getPenThickness() * (
                               self.screen.getHeightScale() + self.screen.getWidthScale()) / 2)
        if len(msg) == 2:
            self.round_line(self.pen.getColor(), self.getUniquePos(msg[0]), self.getUniquePos(msg[1]),
                            self.pen.getPenThickness() * (
                                    self.screen.getHeightScale() + self.screen.getWidthScale()) / 2)

    def cmd_countdown(self, msg):
        # When a request is received from the server - updates the timer for all players except the painter.
        self.counter = int(msg[0])

    def cmd_isPainter(self):
        # When a request is received from the server - sends to draw the fact that he drew and saves it in the game system.
        self.player.setIsPainter(True)

    def cmd_doClear(self):
        # When a request is received from the server - clears the board for all players except the painter.
        self.screen.getScreen().fill((255, 255, 255))
        self.screen.blit(guesser_interface, (0, 0))

    def cmd_startGame(self, msg):
        # When a request is received from the server - starts the game.
        global draw_on
        self.rounds_left = 6
        draw_on = False
        self.painter = msg[1]
        if self.client_id == msg[0]:
            self.player.setIsPainter(True)
        else:
            self.player.setIsPainter(False)
        self.player.setScore(0)

        self.game_page = 'In_Mid_Game'

    def cmd_gamePrep(self, msg):
        # When a request is received from the server - updates stuff before the game starts.
        del msg[0][0]
        self.nick_list = msg[0]
        self.active_conns = len(self.nick_list)
        self.words = msg[1]
        self.lobby_owner_id = msg[2]
        self.game_page = 'In_Pre_Game'

    def cmd_lobbySpecs(self, msg):
        # When a request is received from the server - updates the existing lobby items / disconnects from the server.
        if self.game_page == 'In_Lobby_Picker' and self.connected:
            self.lobby_list = msg
        elif not self.connected:
            self.close()

    # Game manager ----------------------------------------------- #
    def game_manager(self):
        # Manages the transition between windows while receiving commands from the server at any given moment.
        global timer_event
        if not self.connected:
            self.connect()
        if self.connected:
            time_delay = 1000
            timer_event = pg.USEREVENT + 1
            pg.time.set_timer(timer_event, time_delay)
        start_thread = True
        while self.connected:
            try:
                for event in pg.event.get():
                    self.pos, self.rel = pg.mouse.get_pos(), pg.mouse.get_rel()
                    if self.game_page == 'In_Lobby_Picker':
                        self.lobby_picker_gui(event)

                    elif self.game_page == 'In_Pre_Game':
                        self.pre_game_gui(event)

                    elif self.game_page == 'In_Mid_Game':
                        self.mid_game_gui(event)

                    elif self.game_page == 'In_End_Game':
                        self.end_game_gui(event)

                    if self.game_page != 'In_Lobby_Picker': self.general_gui(event)
                    self.music.display_icon(self.screen, mute_on, mute_off)
                    self.screen.update()

                if start_thread:
                    self.thread = Thread(target=self.handle_game)
                    self.thread.start()
                    start_thread = False
                    self.send('LOBBIES_SPECS')

            except Exception as e:
                print(e)
                pass

        self.thread.join()
        self.close()

    # Game graphical user interface functions -------------------- #
    def lobby_picker_gui(self, event):
        # The inlay window interface for lobbies.
        self.screen.blit(lobby_picker_background, (0, 0))
        lobby_name_box.run(event, 'SAVE')
        self.checkmark_handler(event)
        tmp_list_len = self.lobby_list_specs_handler(event)
        # Music button ------------------------------------------- #
        if 29 * self.screen.getWidthScale() < self.pos[0] < 147 * self.screen.getWidthScale() \
                and 31 * self.screen.getHeightScale() < self.pos[1] < 117 * self.screen.getHeightScale():
            self.music_button(event)

        # Create button ------------------------------------------ #
        elif 126 * self.screen.getWidthScale() < self.pos[0] < 436 * self.screen.getWidthScale() \
                and 908 * self.screen.getHeightScale() < self.pos[1] < 990 * self.screen.getHeightScale():
            self.create_lobby_button(event)

        # Join button -------------------------------------------- #
        elif 479 * self.screen.getWidthScale() < self.pos[0] < 654 * self.screen.getWidthScale() \
                and 908 * self.screen.getHeightScale() < self.pos[1] < 990 * self.screen.getHeightScale():
            self.join_lobby_button(event)

        # Hide full lobbies check mark --------------------------- #
        elif 1268 * self.screen.getWidthScale() < self.pos[0] < 1292 * self.screen.getWidthScale() \
                and 917 * self.screen.getHeightScale() < self.pos[1] < 939 * self.screen.getHeightScale():
            self.hide_full_lobbies_checkmark(event)

        # Hide locked lobbies check mark ------------------------- #
        elif 1268 * self.screen.getWidthScale() < self.pos[0] < 1292 * self.screen.getWidthScale() \
                and 954 * self.screen.getHeightScale() < self.pos[1] < 978 * self.screen.getHeightScale():
            self.hide_locked_lobbies_checkmark(event)

        # Password check mark ------------------------------------ #
        elif 712 * self.screen.getWidthScale() < self.pos[0] < 735 * self.screen.getWidthScale() \
                and 954 * self.screen.getHeightScale() < self.pos[1] < 977 * self.screen.getHeightScale():
            self.lobby_password_checkmark(event)

        # Up arrow button ---------------------------------------- #
        elif 1723 * self.screen.getWidthScale() < self.pos[0] < 1783 * self.screen.getWidthScale() \
                and 886 * self.screen.getHeightScale() < self.pos[1] < 933 * self.screen.getHeightScale():
            self.up_arrow_button(event, tmp_list_len)

        # Down arrow button ---------------------------------------- #
        elif 1723 * self.screen.getWidthScale() < self.pos[0] < 1783 * self.screen.getWidthScale() \
                and 962 * self.screen.getHeightScale() < self.pos[1] < 1007 * self.screen.getHeightScale():
            self.down_arrow_button(event, tmp_list_len)

        # Back button -------------------------------------------- #
        elif 1538 * self.screen.getWidthScale() < self.pos[0] < 1600 * self.screen.getWidthScale() and 888 * \
                self.screen.getHeightScale() < self.pos[1] < 996 * self.screen.getHeightScale() \
                or 1596 * self.screen.getWidthScale() < self.pos[0] < 1645 * self.screen.getWidthScale() and 913 * \
                self.screen.getHeightScale() < self.pos[1] < 971 * self.screen.getHeightScale() \
                or 1644 * self.screen.getWidthScale() < self.pos[0] < 1679 * self.screen.getWidthScale() and 936 * \
                self.screen.getHeightScale() < self.pos[1] < 999 * self.screen.getHeightScale():
            self.screen.blit(lobby_picker_back_icon, (0, 0))
            self.back_button(event)

        # Quit mechanism/button -------------------------------------- #
        elif event.type == pg.QUIT:
            self.close()
            time.sleep(2)
            pg.quit()
            sys.exit()

        else:
            hover_sound.reset()
            click_sound.reset()
            error_sound.reset()

    def general_gui(self, event):
        # General interface.
        chat_input_box.run(event, 'SEND')
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                if chat_input_box.getText() != '':
                    chat_msg = ' '.join([x for x in chat_input_box.getText().split(' ') if len(x) > 0])
                    if chat_msg.lower() == self.words[
                        0] and not self.player.getGuessed() and not self.player.getIsPainter():
                        self.send(['CHAT_MSG', f'{self.player.getNickname()} has guessed the word!          '])
                        self.player.setGuessed(True)
                        chat_input_box.setText('')
                        self.player.setScore(
                            self.player.getScore() + int(self.counter / (self.player.getNumOfGuessers() + 1)))
                        self.send(['SCORE', self.player.getScore()])

                    elif chat_msg.lower() != self.words[0]:
                        self.send(['CHAT_MSG', f'{self.player.getNickname()}: {chat_msg}'])

                    elif chat_msg.lower() == self.words[
                        0] and self.player.getGuessed() or self.player.getIsPainter():
                        self.send(['CHAT_MSG', f'{self.player.getNickname()}: {"*" * len(chat_msg)}'])
                    chat_input_box.setText('')

        self.draw_game_info(self.painter)
        self.music.display_icon(self.screen, mute_on, mute_off)
        self.nick_organizer()
        self.chat_organizer()

        # Music button ----------------------------------------------- #
        if 29 * self.screen.getWidthScale() < self.pos[0] < 147 * self.screen.getWidthScale() \
                and 31 * self.screen.getHeightScale() < self.pos[1] < 117 * self.screen.getHeightScale():
            self.music_button(event)

        # Quit mechanism/button -------------------------------------- #
        elif 71 * self.screen.getWidthScale() < self.pos[0] < 207 * self.screen.getWidthScale() and 32 * \
                self.screen.getHeightScale() < self.pos[1] < 112 * self.screen.getHeightScale() \
                or 207 * self.screen.getWidthScale() < self.pos[
            0] < 270 * self.screen.getWidthScale() and 58 * \
                self.screen.getHeightScale() < self.pos[1] < 89 * self.screen.getHeightScale() \
                or 251 * self.screen.getWidthScale() < self.pos[
            0] < 276 * self.screen.getWidthScale() and 89 * \
                self.screen.getHeightScale() < self.pos[1] < 113 * self.screen.getHeightScale():
            self.screen.blit(back_icon, (0, 0))
            self.back_button(event)

        elif event.type == pg.QUIT:
            self.close()
            time.sleep(2)
            pg.quit()
            sys.exit()
        else:
            hover_sound.reset()
            click_sound.reset()

    def pre_game_gui(self, event):
        # Pre-game interface.
        if self.active_conns >= 2:
            if self.client_id == self.lobby_owner_id:
                self.screen.blit(start_game_interface, (0, 0))
                if 732 * self.screen.getWidthScale() < self.pos[0] < 1096 * self.screen.getWidthScale() \
                        and 936 * self.screen.getHeightScale() < self.pos[1] < 1047 * self.screen.getHeightScale():
                    self.start_button(event)
            else:
                self.screen.blit(waiting_for_owner_to_start_interface, (0, 0))
        else:
            self.screen.blit(waiting_for_players_interface, (0, 0))

    def mid_game_gui(self, event):
        # Mid-game interface.
        if self.active_conns >= 2:
            if self.rounds_left > 0:
                if self.player.getIsPainter():
                    self.painter_gui(event)
                    self.painter_func(event)

                else:
                    self.guesser_gui()
            else:
                time.sleep(0.2)
                self.send('ANNOUNCE_WINNER')
        else:
            time.sleep(0.2)
            self.send('ANNOUNCE_WINNER')

    def end_game_gui(self, event):
        # End-game interface.
        if self.counter > 0:
            winner_sound.play_sound_static()
            self.screen.blit(empty_interface, (0, 0))
            self.screen.draw_text(f'{self.winner.upper()} IS THE WINNER!', (255, 142, 36),
                                  'assets\\fonts\\Dosis-ExtraBold.ttf',
                                  188, 365, 477)
            if event.type == timer_event:
                self.counter -= 12
        else:
            winner_sound.setPlay(True)
            self.counter = 60
            self.screen.blit(empty_interface, (0, 0))
            self.game_page = 'In_Pre_Game'

    def painter_gui(self, event):
        # Painter interface.
        pg.draw.rect(self.screen.getScreen(), self.pen.getColor(), (400 * self.screen.getWidthScale(),
                                                                    939 * self.screen.getHeightScale(),
                                                                    200 * self.screen.getWidthScale(),
                                                                    1030 * self.screen.getHeightScale()))
        self.screen.blit(painter_interface, (0, 0))
        # Pen Implement ---------------------------------------------- #
        if 1335.5 * self.screen.getWidthScale() < self.pos[0] < 1378.5 * self.screen.getWidthScale() \
                and 970 * self.screen.getHeightScale() < self.pos[1] < 1024 * self.screen.getHeightScale():
            self.pen_button(event)
        # Eraser Implement ------------------------------------------- #
        elif 1270 * self.screen.getWidthScale() < self.pos[0] < 1320 * self.screen.getWidthScale() \
                and 970 * self.screen.getHeightScale() < self.pos[1] < 1024 * self.screen.getHeightScale():
            self.erase_button(event)

        # Fill Implement --------------------------------------------- #
        elif 1218.5 * self.screen.getWidthScale() < self.pos[0] < 1253.5 * self.screen.getWidthScale() \
                and 970 * self.screen.getHeightScale() < self.pos[1] < 1024 * self.screen.getHeightScale():
            self.fill_button(event)

        # Clear Implement -------------------------------------------- #
        elif 1035.5 * self.screen.getWidthScale() < self.pos[0] < 1075.5 * self.screen.getWidthScale() \
                and 970 * self.screen.getHeightScale() < self.pos[1] < 1024 * self.screen.getHeightScale():
            self.clear_button(event)

        # Pen thickness increase ------------------------------------- #
        elif 1095.5 * self.screen.getWidthScale() < self.pos[0] < 1135.5 * self.screen.getWidthScale() \
                and 970 * self.screen.getHeightScale() < self.pos[1] < 1024 * self.screen.getHeightScale():
            self.thickness_increase(event)

        # Pen thickness decrease ------------------------------------- #
        elif 1155.5 * self.screen.getWidthScale() < self.pos[0] < 1195.5 * self.screen.getWidthScale() \
                and 970 * self.screen.getHeightScale() < self.pos[1] < 1032 * self.screen.getHeightScale():
            self.thickness_decrease(event)

        # Pen color picker ------------------------------------------- #
        elif 538 * self.screen.getWidthScale() < self.pos[0] < 1000 * self.screen.getWidthScale() \
                and 933 * self.screen.getHeightScale() < self.pos[1] < 1060 * self.screen.getHeightScale():
            self.color_picker(event)
        else:
            pen_sound.reset()

        if self.player.getPenClicked():
            self.pen_func(event)

        elif self.player.getEraserClicked():
            self.erase_func(event)

        elif self.player.getFillClicked():
            self.fill_func(event)

    def guesser_gui(self):
        # Guesser interface.
        self.screen.blit(guesser_interface, (0, 0))
        self.draw_countdown(self.counter)
        self.screen.draw_text(str('_ ' * len(self.words[0])).upper(), (255, 255, 255),
                              'assets\\fonts\\ACETONE.ttf',
                              100, 780, 42)

    def nick_organizer(self):
        # Displays all nicknames and punctuation on the left side of the screen.
        y = 200
        for i in range(len(self.nick_list)):
            size = 190
            size -= 13 * len(self.nick_list[i][0])
            self.screen.draw_text(self.nick_list[i][0], (45, 62, 80), 'assets\\fonts\\Nickname DEMO.otf', size, 40, y)
            if self.game_page == 'In_Mid_Game':
                self.screen.draw_text(f'Score: {self.nick_list[i][1]}', (45, 62, 80),
                                      'assets\\fonts\\Nickname DEMO.otf', 40,
                                      245,
                                      y + 80)
            if self.active_conns != len(self.nick_list):
                self.active_conns = len(self.nick_list)
            y += 146

    def chat_organizer(self):
        # Arranges the order of the chat messages.
        global y, z
        y = 160
        if len(self.chat_list) <= 20:
            for z in range(len(self.chat_list)):
                self.draw_chat()
        else:
            for z in range(len(self.chat_list) - 20, len(self.chat_list)):
                self.draw_chat()

    def draw_chat(self):
        # Displays the chat messages on the right side of the screen.
        global y, z
        color = (45, 62, 80)
        if 'has guessed the word!          ' in self.chat_list[z]:
            color = (79, 232, 19)
        self.screen.draw_text(self.chat_list[z], color, 'assets\\fonts\\Dosis-ExtraBold.ttf', 35, 1460, y)
        y += 38

    def draw_countdown(self, num):
        # Displays the timer.
        self.screen.blit(timer_icon, (0, 0))
        self.screen.draw_text(str(num), (255, 255, 255), 'assets\\fonts\\ACETONE.ttf',
                              70, 461, 42)

    def draw_game_info(self, painter):
        # Displays the number of remaining rounds and the current painter.
        if self.rounds_left > 0 and self.game_page == 'In_Mid_Game':
            self.screen.draw_text(f'ROUNDS LEFT: {self.rounds_left}', (255, 255, 255), 'assets\\fonts\\JungleAdventurer.ttf',
                                  55, 1444, 1005)
            self.screen.draw_text(f'PAINTER: {painter}', (255, 255, 255), 'assets\\fonts\\JungleAdventurer.ttf',
                                  55, 1444, 1042)

    # Painter functions ------------------------------------------ #
    def painter_func(self, event):
        # The function of the painter and all its functions.
        if self.counter > 0:
            self.send(self.pen)
            self.draw_countdown(self.counter)
            self.screen.draw_text(str(self.words[0]).upper(), (255, 255, 255), 'assets\\fonts\\Dosis-ExtraBold.ttf',
                                  100, 818, 25)

            if event.type == timer_event:
                if self.player.getNumOfGuessers() == len(self.nick_list) - 1:
                    self.send(['COUNTDOWN', 0])
                    self.counter = 0
                else:
                    self.send(['COUNTDOWN', self.counter - 1])
                    self.counter -= 1

        else:
            self.pen = Pen()
            self.send(self.pen)
            self.player.setScore(
                self.player.getScore() + int((self.player.getNumOfGuessers()) * (120 / self.active_conns - 1)))
            self.player.setIsPainter(False)
            time.sleep(0.2)
            self.send(['ROUND_OVER', self.player.getScore()])

        self.board_x = 415 * self.screen.getWidthScale(), 1420 * self.screen.getWidthScale()
        self.board_y = 100 * self.screen.getHeightScale(), 925 * self.screen.getHeightScale()

    def fill_func(self, event):
        # The painter's bucket filling function.
        self.screen.blit(fill_button_clicked, (0, 0))
        if self.board_x[0] < self.pos[0] < self.board_x[1] and self.board_y[0] < self.pos[1] < self.board_y[1]:
            if event.type == pg.MOUSEBUTTONDOWN:
                self.pen.flood_fill(self.screen, self.pos)
                self.send(['DO_FILL', self.getUniversalPos(self.pos)])

    def pen_func(self, event):
        # The painter's pen function.
        self.screen.blit(pen_button_clicked, (0, 0))
        self.draw(event)

    def erase_func(self, event):
        # The painter's erase function.
        self.screen.blit(erase_button_clicked, (0, 0))
        self.draw(event)

    def chat_func(self, event):
        # Chat writing function.
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                if chat_input_box.getText() != '':
                    chat_msg = chat_input_box.getText()
                    if chat_msg.lower() == self.words[
                        0] and not self.player.getGuessed() and not self.player.getIsPainter():
                        self.send(['CHAT_MSG', f'{self.player.getNickname()} has guessed the word!          '])
                        self.player.setGuessed(True)
                        chat_input_box.setText('')
                        self.player.setScore(
                            self.player.getScore() + int(self.counter / (self.player.getNumOfGuessers() + 1)))

                    elif chat_msg.lower() != self.words[0]:
                        self.send(['CHAT_MSG', f'{self.player.getNickname()}: {chat_msg}'])

                    elif chat_msg.lower() == self.words[
                        0] and self.player.getGuessed() or self.player.getIsPainter():
                        self.send(['CHAT_MSG', f'{self.player.getNickname()}: {"*" * len(chat_msg)}'])
                    chat_input_box.setText('')

    # Buttons functions ------------------------------------------ #
    def music_button(self, event):
        # The button that controls the music (on / off).
        hover_sound.play_sound_static()
        if self.music.getPlay():
            self.screen.blit(mute_on_clicked, (0, 0))
        else:
            self.screen.blit(mute_off_clicked, (0, 0))
        click_sound.play_sound(event)
        self.music.play_music(event)

    def pen_button(self, event):
        # The button that selects the pen function.
        if not self.player.getPenClicked():
            pen_sound.play_sound_static()
            self.screen.blit(pen_button_clicked, (0, 0))
            if event.type == pg.MOUSEBUTTONDOWN:
                click_sound.play_sound(event)
                self.player.setPenClicked(True)
                self.pen.setColor((0, 0, 0))

    def fill_button(self, event):
        # The button that selects the Fill Bucket function.
        if not self.player.getFillClicked():
            pen_sound.play_sound_static()
            self.screen.blit(fill_button_clicked, (0, 0))
            if event.type == pg.MOUSEBUTTONDOWN:
                click_sound.play_sound(event)
                self.player.setFillClicked(True)

    def erase_button(self, event):
        # The button that selects the eraser function.
        if not self.player.getEraserClicked():
            pen_sound.play_sound_static()
            self.screen.blit(erase_button_clicked, (0, 0))
            if event.type == pg.MOUSEBUTTONDOWN:
                click_sound.play_sound(event)
                self.player.setEraserClicked(True)
                self.pen.setColor((255, 255, 255))

    def clear_button(self, event):
        # The button that cleans the board.
        pen_sound.play_sound_static()
        if event.type == pg.MOUSEBUTTONDOWN:
            self.send('DO_CLEAR')
            click_sound.play_sound(event)
            self.screen.getScreen().fill((255, 255, 255))
            self.screen.blit(painter_interface, (0, 0))
        self.screen.blit(clear_button_clicked, (0, 0))

    def color_picker(self, event):
        # The color selection button.
        if self.screen.getScreen().get_at(self.pos) is not (255, 255, 255, 255):
            pg.draw.rect(self.screen.getScreen(), self.screen.getScreen().get_at(self.pos),
                         (400 * self.screen.getWidthScale(),
                          939 * self.screen.getHeightScale(),
                          200 * self.screen.getWidthScale(),
                          1030 * self.screen.getHeightScale()))
            self.screen.blit(painter_interface, (0, 0))
            if event.type == pg.MOUSEBUTTONDOWN:
                self.pen.setColor(self.screen.getScreen().get_at(self.pos))
                click_sound.play_sound(event)

    def back_button(self, event):
        # The "Back" button function - pressing takes the user to the main menu window.
        hover_sound.play_sound_static()
        if event.type == pg.MOUSEBUTTONDOWN:
            click_sound.play_sound(event)
            self.connected = False
            self.close()

    def create_lobby_button(self, event):
        # The "Create" button function - Clicking takes the client to a new game lobby he has created.
        hover_sound.play_sound_static()
        self.screen.blit(create_icon_clicked, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN:
            self.create_lobby_func(event)

    def join_lobby_button(self, event):
        # The "Join" button function - pressing moves the client to an existing lobby he has chosen to enter.
        hover_sound.play_sound_static()
        self.screen.blit(join_icon_clicked, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN:
            self.join_lobby_func(event)

    def up_arrow_button(self, event, tmp_list_len):
        # Up Arrow Button - Click to scroll up the list of available lobbies.
        if event.type == pg.MOUSEBUTTONDOWN:
            if tmp_list_len > 11:
                if self.lobby_picker_arrows_pos > 0:
                    self.lobby_picker_arrows_pos -= 1
            else:
                self.lobby_picker_arrows_pos = 0

    def down_arrow_button(self, event, tmp_list_len):
        # Down Arrow Button - Click to scroll down the list of available lobbies.
        if event.type == pg.MOUSEBUTTONDOWN:
            if tmp_list_len > 11:
                if self.lobby_picker_arrows_pos < tmp_list_len - 11:
                    self.lobby_picker_arrows_pos += 1
            else:
                self.lobby_picker_arrows_pos = 0

    def start_button(self, event):
        # Function intended for a lobby manager - when clicking starts the game.
        self.screen.blit(owner_start_game_clicked_icon, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN:
            print(self.pos)
            click_sound.play_sound(event)
            self.send('START_GAME')

    # Pen functions ---------------------------------------------- #
    def round_line(self, color, start, end=(0, 0), radius=10):
        # Function for drawing a rounded line - Used by the pen function of the painter.
        if self.player.getIsPainter():
            self.send(['DRAW', self.getUniversalPos(start), self.getUniversalPos(end)])
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = max(abs(dx), abs(dy))
        for i in range(distance):
            x = int(start[0] + float(i) / distance * dx)
            y = int(start[1] + float(i) / distance * dy)
            pg.draw.circle(self.screen.getScreen(), color, (x, y), radius)

    def draw(self, event):
        # Function To operate the pen function of the painter.
        global draw_on, last_pos
        if self.board_x[0] < self.pos[0] < self.board_x[1] and self.board_y[0] < self.pos[1] < self.board_y[1]:
            if event.type == pg.MOUSEBUTTONDOWN:
                pg.draw.circle(self.screen.getScreen(), self.pen.getColor(), self.pos,
                               self.pen.getPenThickness() * (self.screen.getHeightScale() +
                                                             self.screen.getWidthScale()) / 2)
                self.send(['DRAW', self.getUniversalPos(self.pos)])
                draw_on = True

            if event.type == pg.MOUSEBUTTONUP:
                draw_on = False
            if event.type == pg.MOUSEMOTION:
                if draw_on:
                    pg.draw.circle(self.screen.getScreen(), self.pen.getColor(), self.pos,
                                   self.pen.getPenThickness() * (
                                           self.screen.getHeightScale() + self.screen.getWidthScale()) / 2)
                    self.round_line(self.pen.getColor(), self.pos, last_pos, self.pen.getPenThickness()
                                    * (self.screen.getHeightScale() + self.screen.getWidthScale()) / 2)

                last_pos = self.pos

        else:
            draw_on = False

    def thickness_increase(self, event):
        # Magnifier Button Function - Increases pen size.
        pen_sound.play_sound_static()
        self.screen.blit(up_button_clicked, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.pen.getPenThickness() <= 45:
                click_sound.play_sound(event)
                self.pen.setPenThickness(self.pen.getPenThickness() + 3)

    def thickness_decrease(self, event):
        # Reduction Button Function - Reduces pen size.
        pen_sound.play_sound_static()
        self.screen.blit(down_button_clicked, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.pen.getPenThickness() >= 7:
                click_sound.play_sound(event)
                self.pen.setPenThickness(self.pen.getPenThickness() - 3)

    # Lobby picker graphical user interface ---------------------- #
    def lobby_password_handle(self, event):
        # A function that manages the password in the lobby assignment window.
        if self.lobby_specs[1] is None:
            self.screen.blit(password_cover, (0, 0))
        else:
            self.screen.blit(password_checkmark, (0, 0))
            lobby_password_box.run(event, 'SAVE')
            self.lobby_specs[1] = lobby_password_box.getText()

    def hide_full_lobbies_handle(self):
        # Function that displays ✔ in the check box for hiding full lobbies - at the client's request.
        if self.lobby_filters[0]:
            self.screen.blit(hide_full_lobbies_checkmark, (0, 0))

    def hide_locked_lobbies_handle(self):
        # Function that displays ✔ in the check box for hiding private lobbies - at the client's request.
        if self.lobby_filters[1]:
            self.screen.blit(hide_locked_lobbies_checkmark, (0, 0))

    def lobby_password_checkmark(self, event):
        # Function that displays ✔ in the Password check box - at the client's request.
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.lobby_specs[1] is None:
                self.lobby_specs[1] = lobby_password_box.getText()
            else:
                self.lobby_specs[1] = None

    def hide_full_lobbies_checkmark(self, event):
        # Function that manages the check box for hiding full lobbies.
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.lobby_filters[0]:
                self.lobby_filters[0] = False
            else:
                self.lobby_filters[0] = True
            self.lobby_picker_arrows_pos = 0

    def hide_locked_lobbies_checkmark(self, event):
        # Function that manages the check box for hiding private lobbies.
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.lobby_filters[1]:
                self.lobby_filters[1] = False
            else:
                self.lobby_filters[1] = True
            self.lobby_picker_arrows_pos = 0

    def checkmark_handler(self, event):
        # A function that manages all check boxes.
        self.lobby_specs[0] = lobby_name_box.getText()
        self.lobby_password_handle(event)
        self.hide_full_lobbies_handle()
        self.hide_locked_lobbies_handle()

    def create_lobby_func(self, event):
        # The "create" function.
        self.send('LOBBIES_SPECS')
        name = ' '.join([x for x in self.lobby_specs[0].split(' ') if len(x) > 0])
        password = self.lobby_specs[1]
        count = 0
        for lobby in self.lobby_list:
            if name == lobby[0][:len(name)]:
                count += 1
        if name != '':
            click_sound.play_sound(event)
            if count > 0:
                name += f' ({count})'
            if password == '':
                password = None
            self.player.setScore(0)
            self.send(['CREATE_LOBBY', name, password])
        else:
            error_sound.play_sound(event)

    def join_lobby_func(self, event):
        # The "join" function.
        name = self.lobby_specs[0]
        password = self.lobby_specs[1]
        if name != '':
            if password == '':
                password = None
            self.player.setScore(0)
            self.send(['JOIN_LOBBY', name, password])
        else:
            error_sound.play_sound(event)

    def draw_lobby_list(self, lobby, color, event):
        # Displays the list of available lobbies on the screen.
        global y, z
        self.screen.draw_text(str(lobby[0]), color, 'assets\\fonts\\ChildrenSans.ttf', 80, 130, y)
        self.screen.draw_text(f'Owner: {str(lobby[1]).upper()}', color, 'assets\\fonts\\ChildrenSans.ttf', 80, 1120, y)
        self.screen.draw_text(f'{str(lobby[2])} / 6', color, 'assets\\fonts\\ChildrenSans.ttf', 90, 1674, y)
        if 117 * self.screen.getWidthScale() < self.pos[0] < 1801 * self.screen.getWidthScale() \
                and (y - 2) * self.screen.getHeightScale() < self.pos[1] < (y + 47) * self.screen.getHeightScale():
            if event.type == pg.MOUSEBUTTONDOWN:
                lobby_name_box.setText(str(lobby[0]))
        y += 50
        z += 50

    def filter_lobby_list(self, tmp_list):
        # Unwanted lobbies filter function from the list of lobbies (customized by the client)
        for lobby in self.lobby_list:
            if lobby[4] != 'ACTIVE':
                if self.lobby_filters[0] and not self.lobby_filters[1]:  # [True, False]
                    if lobby[2] < 6:
                        tmp_list.append(lobby)

                elif not self.lobby_filters[0] and self.lobby_filters[1]:  # [False, True]
                    if not lobby[3]:
                        tmp_list.append(lobby)

                elif self.lobby_filters[0] and self.lobby_filters[1]:  # [True, True]
                    if lobby[2] < 6 and not lobby[3]:
                        tmp_list.append(lobby)

                elif not self.lobby_filters[0] and not self.lobby_filters[1]:  # [False, False]
                    tmp_list.append(lobby)

                if lobby in tmp_list:
                    if str(lobby_name_box.getText()) == '':
                        pass
                    elif str(lobby_name_box.getText()) != str(lobby[0])[:len(str(lobby_name_box.getText()))]:
                        tmp_list.remove(lobby)
        return tmp_list

    def lobby_list_specs_handler(self, event):
        # Function that arranges the lobbies according to the arrow buttons (customized by the client)
        global y, z
        y = 315
        z = 0
        color = (255, 255, 255)
        tmp_list = []
        tmp_list = self.filter_lobby_list(tmp_list)
        tmp_list_original_len = len(tmp_list)

        if len(tmp_list) > 11:
            tmp_list = tmp_list[self.lobby_picker_arrows_pos:self.lobby_picker_arrows_pos + 11]
        for lobby in tmp_list:
            if lobby is not None:
                if lobby[3] is True:
                    self.screen.blit(lock_icon, (0, 0 + z))
                self.draw_lobby_list(lobby, color, event)
        return tmp_list_original_len
