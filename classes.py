#!/usr/bin/python3.7.4
# Setup Python ----------------------------------------------- #
import cv2
import pygame as pg
from pygame import mixer
import os
import uuid
from random import sample


# Setup classes ---------------------------------------------- #
class PgSetup(object):
    # Constructor ------------------------------------------------ #
    def __init__(self, WIDTH, HEIGHT):
        # Creates the screen object itself - gets the length and width of the screen.
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.init()
        pg.key.set_repeat(150, 350)
        pg.font.init()
        pg.display.set_caption('DrawGuess_Client')
        pg.display.set_icon(pg.image.load('assets\\images\\icons\\programicon.png'))
        self.clock = pg.time.Clock()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.resolution_options = ['640 x 360', '768 x 432', '960 x 540',
                                   '1280 x 720', '1600 x 900', '1920 x 1080']
        if f'{WIDTH} x {HEIGHT}' not in self.resolution_options:
            self.WIDTH = 960
            self.HEIGHT = 540
        else:
            self.WIDTH = WIDTH
            self.HEIGHT = HEIGHT

        self.IDEAL_WIDTH = 1920
        self.IDEAL_HEIGHT = 1080
        self.width_scale = self.WIDTH / self.IDEAL_WIDTH
        self.height_scale = self.HEIGHT / self.IDEAL_HEIGHT

    # Getters ---------------------------------------------------- #
    def getScreen(self):
        return self.screen

    def getWidthScale(self):
        return self.width_scale

    def getHeightScale(self):
        return self.height_scale

    def getClock(self):
        return self.clock

    def getWidth(self):
        return self.WIDTH

    def getHeight(self):
        return self.HEIGHT

    def getResolutionOptions(self):
        return self.resolution_options

    # Setters ---------------------------------------------------- #
    def setWidth(self, width):
        self.WIDTH = width

    def setHeight(self, height):
        self.HEIGHT = height

    def setScreen(self, width, height):
        self.screen = pg.display.set_mode((width, height))

    # Functions -------------------------------------------------- #
    def update(self, x=None):
        # Updates part of the screen (sometimes the whole) on every event that takes place in the game.
        self.clock.tick(60)
        if x is None:
            pg.display.update()
        else:
            pg.display.update(x)

    def flip(self, tick=60):
        # Updates the entire screen on every event that takes place in the game.
        pg.display.flip()
        self.clock.tick(tick)

    def blit(self, pic, pos):
        # Display images / colors on the screen (depending on the location set by the user).
        pic = pg.transform.scale(pic, (self.WIDTH, self.HEIGHT))
        self.screen.blit(pic, (pos[0] * self.width_scale, pos[1] * self.height_scale))

    def screen_resize(self, width, height):
        # Change the screen aspect ratio (such as image / text size and location, etc.) according to the resolution.
        self.WIDTH = width
        self.HEIGHT = height
        self.width_scale = width / self.IDEAL_WIDTH
        self.height_scale = height / self.IDEAL_HEIGHT
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def draw_text(self, text, color, font, size, x, y):
        # Display text on the screen (depending on the color, size, font and location selected by the user).
        font1 = pg.font.Font(font, int(size * (self.height_scale + self.width_scale / 3) / 2))
        surface = font1.render(text, True, color)
        self.screen.blit(surface, (x * self.width_scale, y * self.height_scale))

    @staticmethod
    def loadify(image):
        # Upload an image to the system as a variable.
        return pg.image.load(image).convert_alpha()

    @staticmethod
    def quit():
        # Closes the screen.
        pg.display.quit()
        pg.font.quit()


class Sound(object):
    # Constructor ------------------------------------------------ #
    def __init__(self, volume, sound, play=True):
        # Creates the sound object - receives the volume and location of the asset from the asset folder from the user.
        self.play = play
        self.sound = mixer.Sound(sound)
        self.volume = volume

        if type(self.volume) == 'int' or 'float':
            self.sound.set_volume(volume)
        else:
            self.sound.set_volume(0.2)

    # Getters ---------------------------------------------------- #
    def getVolume(self):
        return self.volume

    def getPlay(self):
        return self.play

    # Setters ---------------------------------------------------- #
    def setVolume(self, volume):
        self.volume = volume

    def setPlay(self, play):
        self.play = play

    # Functions -------------------------------------------------- #
    def play_sound(self, event):
        # Activates sound according to user action (event).
        if self.play is True:
            if event.type == pg.MOUSEBUTTONDOWN:
                self.sound.play()
                self.play = False
        if event.type == pg.MOUSEBUTTONUP:
            self.play = True

    def play_sound_static(self):
        # Activates sound regardless of user action.
        if self.play is True:
            self.sound.play()
            self.play = False

    def reset(self):
        if self.play is False:
            self.setPlay(True)


class Music:
    # Constructor ------------------------------------------------ #
    def __init__(self, volume, play=True, music='assets\\sounds\\Theme_Music.mp3'):
        # Loads the music from the assets folder and defines the class as the interface music. Gets volume from the user.
        mixer.music.load(music)
        pg.mixer.music.play(-1)
        self.play = play
        self.volume = volume

        if type(self.volume) == 'int' or 'float':
            pg.mixer.music.set_volume(self.volume)
        else:
            pg.mixer.music.set_volume(0.01)

    # Getters ---------------------------------------------------- #
    def getVolume(self):
        return self.volume

    def getPlay(self):
        return self.play

    # Setters ---------------------------------------------------- #
    def setVolume(self, volume):
        if type(self.volume) == 'int' or 'float':
            pg.mixer.music.set_volume(volume)
        else:
            pg.mixer.music.set_volume(0.01)

    # Functions -------------------------------------------------- #
    def play_music(self, event):
        # Activate / stop the music according to the user's decision (event).
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.play is False:
                pg.mixer.music.unpause()
                self.play = True
            else:
                pg.mixer.music.pause()
                self.play = False

    def display_icon(self, screen, icon_mute_on, icon_mute_off):
        # Display the speaker icons (on / off) on the screen.
        if self.play is False:
            screen.blit(icon_mute_on, (0, 0))
        else:
            screen.blit(icon_mute_off, (0, 0))


class InputBox(object):
    # Constructor ------------------------------------------------ #
    def __init__(self, screen, x, y, w, h, font, text_size, active_color, inactive_color, max_str_len=10, border=True,
                 text=''):
        # Creates the text box object - receives from the user the screen, location, length and width, font, text size,
        # color when the box is active and inactive, maximum number of letters and whether the border will be visible (True / False).
        self.screen = screen
        self.w = w
        self.h = h
        self.x = x
        self.y = y

        self.color = active_color
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.border = border
        self.active = False

        self.text = text
        self.text_size = text_size
        self.font_raw = font
        self.max_str_len = max_str_len
        self.font = pg.font.Font(self.font_raw, int(self.text_size * self.screen.getHeightScale()))
        self.txt_surface = self.font.render(self.text, True, self.color)
        self.rect = pg.Rect(self.x * self.screen.getWidthScale(), self.y * self.screen.getHeightScale(), self.w,
                            self.h * self.screen.getHeightScale())

    # Getters ---------------------------------------------------- #
    def getText(self):
        return self.text

    def getActive(self):
        return self.active

    # Setters ---------------------------------------------------- #
    def setFont(self, font):
        self.font = pg.font.Font(font, self.text_size)

    def setTextSize(self, text_size):
        self.text_size = text_size

    def setText(self, text):
        self.text = text

    def setRectY(self, y):
        self.rect = pg.Rect(self.x, y, self.w, self.h)

    # Functions -------------------------------------------------- #
    def handle_event_send(self, event):
        # Writes in the variable "text" the letters received from the user and after pressing the key "Enter" resets the variable.
        self.txt_surface = self.font.render(self.text, True, self.color)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) <= self.max_str_len:
                if event.unicode.encode().isalpha() or event.unicode.isdigit() or event.unicode in "!@#$%^&*()-+?_=,<>/" or event.unicode == ' ':
                    self.text += event.unicode

    def handle_event_save(self, event):
        # Writes in the variable "text" the letters received from the user and after pressing the key "Enter" makes the text box inactive.
        self.resize()
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.active_color if self.active else self.inactive_color

        if self.active:
            self.txt_surface = self.font.render(self.text, True, self.color)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.color = self.inactive_color
                    self.active = False
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif len(self.text) <= self.max_str_len:
                    if event.unicode.encode().isalpha() or event.unicode.isdigit() or event.unicode in "!@#$%^&*()-+?_=,<>/" or event.unicode == ' ':
                        self.text += event.unicode
                # Re-render the text.
        else:
            self.color = self.inactive_color
            self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self, w):
        # Updates the text box size according to the length of the variable.
        width = max(w, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Displays the text box on the screen.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        if self.border:
            pg.draw.rect(screen, self.color, self.rect, 4)

    def run(self, event, action):
        # Runs the text box function in the program itself (send / save depending on the situation)
        if action == 'SAVE':
            self.handle_event_save(event)
        elif action == 'SEND':
            self.handle_event_send(event)
        self.draw(self.screen.getScreen())
        self.update(self.w * self.screen.getWidthScale())

    def resize(self):
        # Resizes the length and width of the text box according to the screen resolution.
        self.font = pg.font.Font(self.font_raw, int(self.text_size * self.screen.getHeightScale()))
        self.txt_surface = self.font.render(self.text, True, self.color)
        self.rect = pg.Rect(self.x * self.screen.getWidthScale(), self.y * self.screen.getHeightScale(),
                            self.w * self.screen.getWidthScale(), self.h * self.screen.getHeightScale())


class Pen(object):
    # Default Constructor ---------------------------------------- #
    def __init__(self):
        # The painter's pen object.
        self.COLOR = (0, 0, 0)
        self.pen_thickness = 10

    # Getters ---------------------------------------------------- #
    def getColor(self):
        return self.COLOR

    def getPenThickness(self):
        return self.pen_thickness

    # Setters ---------------------------------------------------- #
    def setColor(self, COLOR_RGB):
        self.COLOR = COLOR_RGB

    def setPenThickness(self, pen_thickness):
        self.pen_thickness = pen_thickness

    # Functions -------------------------------------------------- #
    def flood_fill(self, screen, pos):
        # Painter bucket filling function.
        arr = pg.surfarray.array3d(screen.getScreen())
        swapPoint = (pos[1], pos[0])
        cv2.floodFill(arr, None, swapPoint, self.COLOR)
        pg.surfarray.blit_array(screen.getScreen(), arr)


class Slider(object):
    # Constructor ------------------------------------------------ #
    def __init__(self, screen, x, y, w, h):
        # Creates the slider object (sliding template) designed to tune the music. Receives from the user the screen,
        # location and length and width of the slider.
        self.screen = screen
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.volume = 50
        self.sliderRect = pg.Rect(self.x * self.screen.getWidthScale(), self.y * self.screen.getHeightScale(),
                                  self.w * self.screen.getWidthScale(), self.h * self.screen.getHeightScale())
        self.circle_x = int(self.x * self.screen.getWidthScale() + self.sliderRect.w / 2)

    # Getters ---------------------------------------------------- #
    def getVolume(self):
        return self.volume

    # Setters ---------------------------------------------------- #
    def setVolume(self, volume):
        self.volume = volume

    # Functions -------------------------------------------------- #
    def draw(self, screen):
        # Displays the slider on the screen.
        pg.draw.rect(screen, (255, 255, 255), self.sliderRect)
        pg.draw.circle(screen, (255, 240, 255), (self.circle_x, (self.sliderRect.h / 2 + self.sliderRect.y)),
                       self.sliderRect.h * 1.5)

    def update_volume(self, x):
        # Updates the volume of the music according to the position of the slider.
        if x < self.sliderRect.x:
            self.volume = 0
        elif x > self.sliderRect.x + self.sliderRect.w:
            self.volume = 100
        else:
            self.volume = int((x - self.sliderRect.x) / float(self.sliderRect.w) * 100)

    def on_slider(self, x, y):
        # Returns True answer if you hover the mouse over the slider.
        if self.on_slider_hold(x, y) or self.sliderRect.x <= x <= \
                self.sliderRect.x + self.sliderRect.w and self.sliderRect.y <= y <= self.sliderRect.y + self.sliderRect.h:
            return True
        else:
            return False

    def on_slider_hold(self, x, y):
        # Returns True answer if the mouse cursor clicks on the slider.
        if ((x - self.circle_x) * (x - self.circle_x) + (y - (self.sliderRect.y + self.sliderRect.h / 2)) * (
                y - (self.sliderRect.y + self.sliderRect.h / 2))) \
                <= (self.sliderRect.h * 1.5) * (self.sliderRect.h * 1.5):
            return True
        else:
            return False

    def handle_event(self, x, y):
        # Operates the slider using the functions mentioned above.
        if self.on_slider_hold(x, y) and pg.mouse.get_pressed()[0] \
                or self.on_slider(x, y) and pg.mouse.get_pressed()[0]:
            if x < self.sliderRect.x:
                self.circle_x = self.sliderRect.x
            elif x > self.sliderRect.x + self.sliderRect.w:
                self.circle_x = self.sliderRect.x + self.sliderRect.w
            else:
                self.circle_x = x
            self.update_volume(x)

        self.draw(self.screen.getScreen())

    def slider_update(self):
        # Updates the size of the slider according to the screen resolution.
        self.sliderRect = pg.Rect(self.x * self.screen.getWidthScale(), self.y * self.screen.getHeightScale(),
                                  self.w * self.screen.getWidthScale(), self.h * self.screen.getHeightScale())
        self.circle_x = int(self.x * self.screen.getWidthScale() + self.sliderRect.w / 2)
        self.volume = 50


class Client(object):
    # Constructor ------------------------------------------------ #
    def __init__(self, client, addr=None):
        # Creates the client object that contains all the details of a particular client.
        # The object receives a client and in some cases an address.
        self.client = client
        self.nickname = ''
        if addr is not None:
            self.addr = addr
        self.index = None
        self.lobby = None
        self.was_painter = False
        self.client_id = str(uuid.uuid4())
        self.client_status = 'In_Lobby_Picker'
        self.score = 0

    def __repr__(self):
        # A function whose function is to print the client's name when printing (instead of the object details)
        return self.nickname

    # Getters ---------------------------------------------------- #
    def getNickname(self):
        return self.nickname

    def getAddr(self):
        return self.addr

    def getClient(self):
        return self.client

    def getLobby(self):
        return self.lobby

    def getIndex(self):
        return self.index

    def getClientID(self):
        return self.client_id

    def getWasPainter(self):
        return self.was_painter

    def getScore(self):
        return self.score

    def getClientStatus(self):
        return self.client_status

    # Setters ---------------------------------------------------- #
    def setIndex(self, index):
        self.index = index

    def setWasPainter(self, was_painter):
        self.was_painter = was_painter

    def setLobby(self, lobby):
        self.lobby = lobby

    def setNickname(self, nickname):
        self.nickname = nickname

    def setScore(self, score):
        self.score = score

    def setClientStatus(self, client_status):
        self.client_status = client_status

    # Functions -------------------------------------------------- #
    def close(self):
        self.client.close()


class Lobby(object):
    # Constructor ------------------------------------------------- #
    def __init__(self, lobby_owner, lobby_name, lobby_password=None):
        # Creates the lobby object that contains all the details of a particular lobby.
        # The object is given a manager name, a lobby name and in some cases a password.
        self.lobby_owner = lobby_owner
        self.lobby_name = lobby_name
        self.lobby_password = lobby_password
        self.game_status = 'INACTIVE'
        self.players_list = [self.lobby_owner]
        self.words = self.getRandomWord(6)

    # Getters ---------------------------------------------------- #
    def getLobbyOwner(self):
        return self.lobby_owner

    def getPlayersList(self):
        return self.players_list

    def getLobbySpecs(self):
        return self.lobby_name, self.lobby_password

    def getGameStatus(self):
        return self.game_status

    def getWords(self):
        return self.words

    # Setters ---------------------------------------------------- #
    def setLobbyOwner(self, owner):
        self.lobby_owner = owner

    def setWords(self, words):
        self.words = words

    def setGameStatus(self, game_status):
        self.game_status = game_status

    # Functions -------------------------------------------------- #
    def appendPlayersList(self, player):
        # A function that expands the list of players in a particular player's lobby.
        self.players_list.append(player)

    def removePlayersList(self, player):
        # A function that removes a particular player from the lobby.
        if player in self.players_list:
            self.players_list.remove(player)

    @staticmethod
    def getRandomWord(x=1):
        # Returns a list of random words from the vocabulary (the number of words is determined by the value x)
        with open('assets\\words.txt', "r") as f:
            words = []
            for line in f:
                words.append(line[0:-1])
        return sample(words, x)


class Player(object):
    # Constructor ------------------------------------------------ #
    def __init__(self, nickname):
        # Creates a player object after connecting to the server - receives a nickname from the user.
        self.IP = '127.0.0.1'
        self.PORT = 5055
        self.nickname = nickname
        self.addr = (self.IP, self.PORT)
        self.score = 0

        self.fill_clicked = False
        self.eraser_clicked = False
        self.pen_clicked = True

        self.isPainter = False
        self.guessed = False
        self.num_of_guessers = 0

    # Getters ---------------------------------------------------- #
    def getAddr(self):
        return self.addr

    def getNickname(self):
        return self.nickname

    def getIsPainter(self):
        return self.isPainter

    def getGuessed(self):
        return self.guessed

    def getNumOfGuessers(self):
        print(self.num_of_guessers)
        return self.num_of_guessers

    def getPenClicked(self):
        return self.pen_clicked

    def getEraserClicked(self):
        return self.eraser_clicked

    def getFillClicked(self):
        return self.fill_clicked

    def getScore(self):
        return self.score

    # Setters ---------------------------------------------------- #
    def setNickname(self, nickname):
        self.nickname = nickname

    def setIsPainter(self, IsPainter):
        self.isPainter = IsPainter

    def setGuessed(self, guessed):
        self.guessed = guessed

    def setNumOfGuessers(self, num_of_guessers):
        self.num_of_guessers = num_of_guessers

    def setPenClicked(self, pen_clicked):
        self.eraser_clicked = False
        self.fill_clicked = False
        self.pen_clicked = pen_clicked

    def setEraserClicked(self, eraser_clicked):
        self.pen_clicked = False
        self.fill_clicked = False
        self.eraser_clicked = eraser_clicked

    def setFillClicked(self, fill_clicked):
        self.pen_clicked = False
        self.eraser_clicked = False
        self.fill_clicked = fill_clicked

    def setScore(self, score):
        self.score = score
