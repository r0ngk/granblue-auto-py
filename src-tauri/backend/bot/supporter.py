from utils.settings import Settings
from utils.message_log import MessageLog as Log
from utils.image_utils_v2 import ImageUtils
from utils.mouse_utils import MouseUtils
from bot.window import Window
from numpy.random import randint

"""
class for generic v2 to handle summon selection
"""
class Supporter:

    @staticmethod 
    def _confirm_page():
        """ Make sure that the bot is at the Summon Selection screen. 
        """
        tries = 10
        while not ImageUtils.confirm_location("select_a_summon"):
            tries -= 1
            if tries <= 0 and ImageUtils.confirm_location("select_a_summon", tries = 1) is False:
                raise Exception("Could not reach the Summon Selection screen.")

    @staticmethod
    def select_summon(summon: str):
        """Find the location of the specified Summon. Will attempt to scroll the screen down to see more Summons if the initial screen position yielded no matches.

        Returns:
            (Tuple[int, int]): Tuple of coordinates of where the center of the Summon is located if image matching was successful. Otherwise, return None.
        """
        # from bot.game import Game
        Supporter._confirm_page()

        if Settings.debug_mode:
            Log.print_message(f"[DEBUG] searching for summon: {summon}")

        # No checking summon elements for this version 
        for _ in range(0,5):

            loc = ImageUtils.find_summon(summon)
            if loc != None:
                MouseUtils.move_and_click_point(
                    loc[0], loc[1], "template_support_summon", mouse_clicks = randint(1,3))
                return True

            if ImageUtils.find_button("bottom_of_summon_selection", tries = 1) is not None:
                MouseUtils.scroll_screen(50,50 - 50, -700)
            else:
                return False
        return False

    @staticmethod
    def _confirm_team():
        # Check for CAPTCHA here. If detected, stop the bot and alert the user.
        Window.check_for_captcha()
        Window.find_click_bttn("ok", tries = 30)
