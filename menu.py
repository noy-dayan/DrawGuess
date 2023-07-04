#!/usr/bin/python3.7.4
# Setup Python ----------------------------------------------- #
import sys
from assets_loader import *
from game import Game
from classes import Slider

# Setup Pygame/menu ------------------------------------------ #
class Menu:
    # Constructor ------------------------------------------------ #
    def __init__(self):
        # Creates the user interface without connecting to the server and displays the main menu.
        self.screen = screen
        self.selected_resolution = f'{self.screen.getWidth()} x {self.screen.getHeight()}'
        self.nickname = ''
        self.running = False
        self.x, self.y = 0, 0
        self.page = 'Main'
        self.music_slider = Slider(self.screen, 765, 655, 391, 15)
        self.music = Music(0.01)
        self.game = Game(self.screen, self.music)

    # Setup run function ----------------------------------------- #
    def run(self):
        # The main function of the department - manages the display of windows and the transition
        # between interfaces (between the interface that is connected to the server and the interface that is not).
        while True:
            try:
                while not self.running:
                    for event in pg.event.get():
                        self.x, self.y = pg.mouse.get_pos()

                        if self.page is 'Main' and self.running is False:
                            self.main_page(event)

                        elif self.page is 'About' and self.running is False:
                            self.about_page(event)

                        elif self.page is 'Settings' and self.running is False:
                            self.settings_page(event)

                        elif self.page is 'Game':
                            self.running = True

                        self.music.display_icon(self.screen, mute_on, mute_off)

                        if event.type == pg.QUIT:
                            pg.quit()
                            sys.exit()
                        self.screen.flip()
                else:
                    try:
                        self.game.game_manager()
                        print('\n' * 100)
                        self.nickname = nickname_box.getText()
                        self.game = Game(self.screen, self.music, self.nickname)
                        self.running = False
                        nickname_box.resize()
                    except Exception as e:
                        self.running = False
                        print(e)

            except Exception as e:
                print(e)
                pass

    # Buttons functions ------------------------------------------ #
    def start_button(self, event):
        # "Start" button function - Clicking activates the function and tries to connect the user
        # to the server as a client, if the connection fails nothing will happen.
        hover_sound.play_sound_static()
        self.screen.blit(start_clicked, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN:
            self.nickname = nickname_box.getText()
            if len(self.nickname) > 0:
                click_sound.play_sound_static()
                if ' ' in self.nickname:
                    self.nickname = self.nickname.replace(' ', '_')
                self.game.setPlayer(self.nickname)
                self.running = True

            else:
                error_sound.play_sound_static()
                error_sound.reset()

    def about_button(self, event):
        # The "About" button function - pressing activates the function and moves the user to the "About" window.
        hover_sound.play_sound_static()
        self.screen.blit(about_clicked, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN:
            click_sound.play_sound(event)
            self.page = 'About'

    def exit_button(self, event):
        # "Exit" button function - when pressed closes the interface.
        hover_sound.play_sound_static()
        self.screen.blit(exit_clicked, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN:
            click_sound.play_sound(event)
            pg.quit()
            sys.exit()

    def music_button(self, event):
        # The button that controls the music (on / off).
        hover_sound.play_sound_static()
        if self.music.getPlay():
            self.screen.blit(mute_on_clicked, (0, 0))
        else:
            self.screen.blit(mute_off_clicked, (0, 0))
        click_sound.play_sound(event)
        self.music.play_music(event)

    def settings_button(self, event):
        # "Settings" button function - Clicking activates the function and takes the user to the "Settings" window.
        hover_sound.play_sound_static()
        self.screen.blit(settings_clicked, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN:
            click_sound.play_sound(event)
            self.page = 'Settings'

    def back_button(self, event):
        # The "Back" button function - pressing takes the user to the main menu window.
        hover_sound.play_sound_static()
        self.screen.blit(back_icon, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN:
            click_sound.play_sound(event)
            self.selected_resolution = f'{self.screen.getWidth()} x {self.screen.getHeight()}'
            self.page = 'Main'

    def left_arrow_button(self, event):
        # The function of the left arrow button inside the settings window is to decrease the screen resolution.
        hover_sound.play_sound_static()
        self.screen.blit(left_settings_arrow, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN and self.screen.getResolutionOptions().index(
                self.selected_resolution) - 1 >= 0:
            self.selected_resolution = self.screen.getResolutionOptions()[
                self.screen.getResolutionOptions().index(self.selected_resolution) - 1]

    def right_arrow_button(self, event):
        # The function of the right arrow button inside the settings window is to increase the screen resolution.
        hover_sound.play_sound_static()
        self.screen.blit(right_settings_arrow, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN and self.screen.getResolutionOptions().index(
                self.selected_resolution) + 1 < len(self.screen.getResolutionOptions()):
            self.selected_resolution = self.screen.getResolutionOptions()[
                self.screen.getResolutionOptions().index(self.selected_resolution) + 1]

    def apply_button(self, event):
        # Save settings button - Pressing saves the selected resolution and changes the screen accordingly.
        hover_sound.play_sound_static()
        self.screen.blit(apply_clicked, (0, 0))
        if event.type == pg.MOUSEBUTTONDOWN and f'{self.screen.getWidth()} x {self.screen.getHeight()}' != self.selected_resolution:
            res = self.selected_resolution.split(' x ')
            self.screen_resize(int(res[0]), int(res[1]))

    # Pages functions -------------------------------------------- #
    def settings_page(self, event):
        # When the window is set to "Settings" - the settings window will appear in addition to all its functions.
        self.screen.blit(settings_background, (0, 0))
        self.music_slider.handle_event(self.x, self.y)
        self.music.setVolume(self.music_slider.getVolume() / 1000)
        self.screen.draw_text(str(self.selected_resolution), (255, 255, 255), 'assets\\fonts\\ChildrenSans.ttf', 100, 838, 445)

        # Music button ----------------------------------------------- #
        if 29 * self.screen.getWidthScale() < self.x < 147 * self.screen.getWidthScale() \
                and 31 * self.screen.getHeightScale() < self.y < 117 * self.screen.getHeightScale():
            self.music_button(event)

        # Left Arrow button ------------------------------------------ #
        elif 726 * self.screen.getWidthScale() < self.x < 793 * self.screen.getWidthScale() \
                and 429 * self.screen.getHeightScale() < self.y < 502 * self.screen.getHeightScale():
            self.left_arrow_button(event)

        # Right Arrow button ----------------------------------------- #
        elif 1128 * self.screen.getWidthScale() < self.x < 1195 * self.screen.getWidthScale() \
                and 429 * self.screen.getHeightScale() < self.y < 502 * self.screen.getHeightScale():
            self.right_arrow_button(event)

        # Apply button ----------------------------------------------- #
        elif 1652 * self.screen.getWidthScale() < self.x < 1875 * self.screen.getWidthScale() \
                and 954 * self.screen.getHeightScale() < self.y < 1026 * self.screen.getHeightScale():
            self.apply_button(event)

        # Back button ------------------------------------------------ #
        elif 150 * self.screen.getWidthScale() < self.x < 207 * self.screen.getWidthScale() and 32 * \
                self.screen.getHeightScale() < self.y < 112 * self.screen.getHeightScale() \
                or 207 * self.screen.getWidthScale() < self.x < 270 * self.screen.getWidthScale() and 58 * \
                self.screen.getHeightScale() < self.y < 89 * self.screen.getHeightScale() \
                or 251 * self.screen.getWidthScale() < self.x < 276 * self.screen.getWidthScale() and 89 * \
                self.screen.getHeightScale() < self.y < 113 * self.screen.getHeightScale():
            self.back_button(event)

        else:
            self.reset()

    def main_page(self, event):
        # When the window is set to "Main" - the main menu window will appear in addition to all its functions.
        self.screen.blit(main_menu_background, (0, 0))
        nickname_box.run(event, 'SAVE')
        # Start button ----------------------------------------------- #
        if 775 * self.screen.getWidthScale() < self.x < 1140 * self.screen.getWidthScale() \
                and 320 * self.screen.getHeightScale() < self.y < 430 * self.screen.getHeightScale():
            self.start_button(event)

        # About button ----------------------------------------------- #
        elif 826 * self.screen.getWidthScale() < self.x < 1090 * self.screen.getWidthScale() \
                and 454 * self.screen.getHeightScale() < self.y < 532 * self.screen.getHeightScale():
            self.about_button(event)

        # Settings button -------------------------------------------- #
        elif 1732 * self.screen.getWidthScale() < self.x < 1883 * self.screen.getWidthScale() \
                and 892 * self.screen.getHeightScale() < self.y < 1043 * self.screen.getHeightScale():
            self.settings_button(event)

        # Quit mechanism/button -------------------------------------- #
        elif 870 * self.screen.getWidthScale() < self.x < 1046 * self.screen.getWidthScale() \
                and 540 * self.screen.getHeightScale() < self.y < 610 * self.screen.getHeightScale():
            self.exit_button(event)

        # Music button ----------------------------------------------- #
        elif 29 * self.screen.getWidthScale() < self.x < 147 * self.screen.getWidthScale() \
                and 31 * self.screen.getHeightScale() < self.y < 117 * self.screen.getHeightScale():
            self.music_button(event)

        else:
            self.reset()

    def about_page(self, event):
        # When the window is set to "About" - the additional items window will appear in addition to all its functions.
        self.screen.blit(about_background, (0, 0))

        # Music button ----------------------------------------------- #
        if 29 * self.screen.getWidthScale() < self.x < 147 * self.screen.getWidthScale() \
                and 31 * self.screen.getHeightScale() < self.y < 117 * self.screen.getHeightScale():
            self.music_button(event)

        # Back button ------------------------------------------------ #
        elif 150 * self.screen.getWidthScale() < self.x < 207 * self.screen.getWidthScale() and 32 * \
                self.screen.getHeightScale() < self.y < 112 * self.screen.getHeightScale() \
                or 207 * self.screen.getWidthScale() < self.x < 270 * self.screen.getWidthScale() and 58 * \
                self.screen.getHeightScale() < self.y < 89 * self.screen.getHeightScale() \
                or 251 * self.screen.getWidthScale() < self.x < 276 * self.screen.getWidthScale() and 89 * \
                self.screen.getHeightScale() < self.y < 113 * self.screen.getHeightScale():
            self.back_button(event)

        else:
            self.reset()

    # Functions -------------------------------------------------- #
    def reset(self):
        # Reset the sounds / text box.
        if nickname_box.getActive():
            self.screen.blit(nickname_clicked, (0, 0))
        hover_sound.reset()
        click_sound.reset()

    def screen_resize(self, w, h):
        # Change the screen aspect ratio (such as image / text size and location, etc.) according to the resolution.
        self.screen.screen_resize(w, h)
        nickname_box.resize()
        chat_input_box.resize()
        self.music_slider.slider_update()
