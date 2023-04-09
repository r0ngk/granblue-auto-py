
from PIL import Image
from typing import List, Tuple
from utils.settings import Settings
from pyautogui import size as get_screen_size, hold, click, write, press
import pyautogui as pya
from utils.message_log import MessageLog as Log
from utils.mouse_utils import MouseUtils as mouse
from utils.image_utils_v2 import ImageUtils
from time import sleep
from numpy.random import randint
import pyperclip

class Window():

    active_area = {}
    window = {}
    sub_window = {}
    extra_window = {}
    window_cnt = 0

    calibration_complete: bool = False
    additional_calibration_required: bool = False
    party_selection_first_run: bool = True
    

    
    @staticmethod
    def goto(url: str, is_sub: bool = False) -> None:
        """is_sub: if use sub window, default to false
        pattern: if match, will not go to the url, default empty
        """
        if is_sub:
            mouse.move_to(Window.sub_start+160, Window.sub_top-55)
        else:
            mouse.move_to(Window.start+160, Window.top-55)
        click()
        sleep(.05)
        pya.hotkey('ctrl', 'a', 'x')
        sleep(.05)
        pyperclip.copy(url)
        pya.hotkey('ctrl', 'v')
        sleep(.05)
        press('enter')

    @staticmethod
    def sub_prepare_loot() -> None:
        """ prepare the support window to be ready to claim loot
        """
        Window.goto("https://game.granbluefantasy.jp/#quest/index",
                    is_sub=True)

    @staticmethod
    def reload(is_sub=False) -> None:
        if is_sub:
            mouse.move_to(Window.sub_start+160, Window.sub_top-55)
        else:
            mouse.move_to(Window.start+160, Window.top-55)
        click()
        press('f5')

    @staticmethod
    def find_click_bttn(bttn: str, tries=5, clicks = randint(1,3)) -> bool:
        """Find and click on an button

        Returns:
            if success
        """
        if Settings.debug_mode:
            Log.print_message(
                f"\n[DEBUG] Attempting to find and click the button: \"{bttn}\".")

        for _ in range(0,tries):

            loc = ImageUtils.find_button(bttn.lower(), tries)
            
            if loc is not None:
                mouse.move_and_click_point(
                    loc[0] + loc[1] + bttn, mouse_clicks = clicks)
                return True

        return False

    @staticmethod
    def calibrate(display_info_check: bool = False) -> None:
        """ Calibrate the dimensions of the game window for fast and accurate \
            image matching.

        Args:
            display_info_check: Displays info of calibration.
        """

        Log.print_message("\n[INFO] Calibrating the dimensions of the window...")
        # sort coordinate from left to right
        home_bttn_coords = sorted(ImageUtils.find_all("home", hide_info=True))
        back_bttn_coords = sorted(ImageUtils.find_all("home_back", hide_info=True))
        
        if len(home_bttn_coords) != len(back_bttn_coords):
            raise RuntimeError(
                "Calibration of window dimensions failed. Some window is partially visible")
        if len(home_bttn_coords) == 0:
            raise RuntimeError(
                "Calibration of window dimensions failed. Is the Home button on the bottom bar visible?")
        if len(back_bttn_coords) == 0:
            raise RuntimeError(
                "Calibration of window dimensions failed. Is the back button visible on the screen?")
        if len(home_bttn_coords) > 2:
            raise RuntimeError(
                "Calibration of window dimensions failed. maximum window is 2")
            
        # calibration base on the side bar
        img = ImageUtils.screenshot()
        for win, coord in enumerate(back_bttn_coords):
            for i in range (coord[0], 2, -1):
                # search left to find 3 consecutive pixels which is the same as side bar
                if img.getpixel((i, coord[1])) == img.getpixel((i-1, coord[1])) == \
                    img.getpixel((i-2, coord[1])) == (31,31,31):
                    # serach up until the color is different
                    for j in range (coord[1], 0, -1):
                        if img.getpixel((i, j)) != (31,31,31):
                            if win==0:
                                Window.window['left'] = i+1
                                Window.window['top'] = j+1
                                Window.window['width'] = home_bttn_coords[win][0] - i+1 + 50
                                Window.window['height'] = back_bttn_coords[win][1] - j+1 + 22
                                Window.window_cnt += 1
                            else:
                                Window.sub_window['left'] = i+1
                                Window.sub_window['top'] = j+1
                                Window.sub_window['width'] = home_bttn_coords[win][0] - i+1 + 50
                                Window.sub_window['height'] = back_bttn_coords[win][1] - j+1 + 22
                                Window.window_cnt += 1
                            break
                    break
        
        ImageUtils.update_window_dimensions(
            Window.window['left'],
            Window.window['top'],
            Window.window['width'], 
            Window.window['height']
            )
        
        if Window.window_cnt > 0:
            Log.print_message("[Calibration] First window has been successfully recalibrated.")
        else:
            raise RuntimeError("Calibration of window dimensions failed, possbily due to side bar")
        if Window.window_cnt > 1:
            Log.print_message("[Calibration] Second window has been successfully recalibrated.")
        else:
            Log.print_message("[INFO] Second Window is not presented")

        
        if display_info_check:
            Log.print_message("\n**********************************************************************")
            Log.print_message("**********************************************************************")
            Log.print_message(f"[INFO] Screen Size: {get_screen_size()}")
            Log.print_message(f"[INFO] Game Window Dimensions: Region({Window.window['left']}, {Window.window['top']}, {Window.window['width']}, {Window.window['height']})")
            if Window.window_cnt > 1:
                Log.print_message(f"[INFO] Game Sub-Window Dimensions: Region({Window.sub_window['left']}, {Window.sub_window['top']}, {Window.sub_window['width']}, {Window.sub_window['height']})")
            Log.print_message("**********************************************************************")
            Log.print_message("**********************************************************************")