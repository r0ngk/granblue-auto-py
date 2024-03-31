from utils.message_log import MessageLog as Log
from utils.settings import Settings
from utils.image_utils import ImageUtils
from utils.mouse_utils import MouseUtils
from bot.window import Window
from bot.combat_mode_v2 import CombatModeV2 as Combat
from utils.parser import Parser
import numpy as np
from time import sleep

class GenericV2:
    """
    Provides more lightweight utility functions with less limitation for more simple mission.
    """

    @staticmethod
    def get_info(raid):
        """ Extract information to start a battle, and load user script
        """
        info = raid['info']
        combact_actions = raid['combact_actions']
        Combat.load_actions(combact_actions)

        url = info.get('url')
        support_summon = [info.get('summon')]
        if support_summon is None:
            support_summon = Settings.summon_list
        repeat = info.get('repeat')
        if repeat is None:
            repeat = Settings.item_amount_to_farm

        return (url, support_summon, repeat)

    @staticmethod
    def start():

        from bot.game import Game
        ImageUtils._summon_selection_first_run = False

        Log.print_message(f"[GenericV2] Parsing combat script: {Settings.combat_script_name}")
        list_of_raids = Parser.parse_raids(Settings.combat_script)

        for raid_id in list_of_raids:

            url, support_summon, repeat = GenericV2.get_info(list_of_raids[raid_id])
        
            Log.print_message(f"[GenericV2] Start battle:{url}, total of {repeat} times")
            Window.goto(url)
            # Window.sub_prepare_loot()
        
            for i in range (1, repeat):
                Log.print_message(f"[GenericV2] Repeat for {i} times")
                GenericV2.single_battle(support_summon)  
                GenericV2.battle_exit_handler(i==1, url)       
                Game._delay_between_runs()
                if (np.random.rand() > .9):
                    Game._move_mouse_security_check()


        Log.print_message(f"GenericV2 successfully finish!")

    @staticmethod
    def single_battle(support_summon):
        from bot.game import Game
        """ Standart method to do a battle
        """
        if not ImageUtils.confirm_location("select_a_summon", tries = 30):
            raise RuntimeError("Failed to arrive at the Summon Selection screen.")
        if not ImageUtils.captcha_pixel_check():
            raise RuntimeError("Abnormal page at summon selection")
        if not Game.select_summon([support_summon], Settings.summon_element_list):
            raise RuntimeError("Failed to select summon")
        if not Game.find_and_click_button("ok", tries = 30, custom_wait=np.random.uniform(0.1,0.5)):
            raise RuntimeError("Failed to confirm team")
        # move to a random place
        MouseUtils.move_to(Window.start+10 + np.random.randint(Window.width-20), 
                           Window.top+10 + np.random.randint(Window.height-100))
        if not Combat.start_combat_mode():
            raise RuntimeError("Failed to start combat mode")

    @staticmethod
    def battle_exit_handler(is_first_time, url):
        """ Exit a battle and prepare for the next
        """
        from bot.game import Game
        if Window.sub_start is None:
            if is_first_time:
                Window.sub_prepare_loot()
            else:
                Combat._sub_back()
            if not ImageUtils.find_button("ok", tries = 30, is_sub=True):
                raise RuntimeError("Failed to reach loot page")
            Game.find_and_click_button("home_back")
        else:
            Combat._reload()
            Window.goto(url)