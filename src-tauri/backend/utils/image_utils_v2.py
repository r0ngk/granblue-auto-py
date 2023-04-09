import os
from datetime import date
from typing import List, Tuple, Optional

import PIL
import cv2
import easyocr
import numpy as np
import pyautogui
from PIL.Image import frombytes
from playsound import playsound

from utils.settings import Settings
from utils.message_log import MessageLog
from mss import mss

class ImageUtils:
    """
    faster Image Utils for generic v2
    """
    sct = mss()
    # Initialize the following for saving screenshots.
    _image_number: int = 0
    _new_folder_name: str = None

    # Used for skipping selecting the Summon Element every time on repeated runs.
    _summon_selection_first_run = True
    _summon_selection_same_element = False

    _match_method: int = cv2.TM_CCOEFF_NORMED
    _match_location: Tuple[int, int] = None
    _custom_scale = Settings.custom_scale

    # Check if the temp folder is created in the images folder.
    _current_dir: str = os.getcwd()
    _temp_dir: str = _current_dir + "/temp/"
    if not os.path.exists(_temp_dir):
        os.makedirs(_temp_dir)

    _reader: easyocr.Reader = None

    @staticmethod
    def screenshot():
        sct_img = ImageUtils.sct.grab(ImageUtils.sct.monitors[1])
        # Create the Image
        img = frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img

    @staticmethod
    def update_window_dimensions(window_left: int, window_top: int, window_width: int, window_height: int, additional_calibration_required: bool = False):
        """Updates the window dimensions for PyAutoGUI to perform faster operations in.

        Args:
            window_left (int): The x-coordinate of the left edge of the region for image matching.
            window_top (int): The y-coordinate of the top edge of the region for image matching.
            window_width (int): The width of the region for image matching.
            window_height (int): The height of the region for image matching.
            additional_calibration_required (bool, optional): Flag that allows for compensation of x-coordinates of all matches to fit the right hand side of the computer screen.

        Returns:
            None
        """
        Settings.window_left = window_left
        Settings.window_top = window_top
        Settings.window_width = window_width
        Settings.window_height = window_height
        Settings.calibration_complete = True
        Settings.additional_calibration_required = additional_calibration_required
        return None

    @staticmethod
    def get_window_dimensions():
        """Get the window dimensions as a Tuple of 4 integers.

        Returns:
            (Tuple[int, int, int, int]): A Tuple of 4 integers consisting of (window_left, window_top, window_width, window_height).
        """
        return Settings.window_left, Settings.window_top, Settings.window_width, Settings.window_height

    @staticmethod
    def _match(template_img, search_area, confidence: float = 0.8):
        """Basic method for template matching

        Returns:
            list of tuples of match location, i.e. (left, top)
        """
        matches = []
        src_img = np.array(ImageUtils.sct.grab(search_area))

        if is_summon:
            # Crop the summon template image so that plus marks would not potentially obscure any match.
            height, width = template_array.shape
            template_array = template_array[0:height, 0:width - int(40 * ImageUtils._custom_scale)]

        result: np.ndarray = cv2.matchTemplate(src_img, template_array, ImageUtils._match_method)
        loc = np.where(result >= confidence)

        if len(loc[0]) != 0:
            for pt in zip(*loc[::-1]):
                matches.append(pt)
            return matches
        return None



    @staticmethod
    def find_button(image_name: str, tries: int = 5):
        """Find the location of the specified button.

        Args:
            image_name (str): Name of the button image file in the /images/buttons/ folder.
            tries (int, optional): Number of tries before failing. Note that this gets overridden if the image_name is one of the adjustments. Defaults to 5.
        Returns:
            (Tuple[int, int]): Tuple of coordinates of where the center of the button is located if image matching was successful. Otherwise, return None.
        """
        if Settings.debug_mode:
            MessageLog.print_message(f"\n[DEBUG] Starting process to find the {image_name.upper()} button image...")

        for _ in range(0,tries):
            result = ImageUtils._match(
                        f"{ImageUtils._current_dir}/images/buttons/{image_name.lower()}.jpg")
            if result != None: return result
        return None


    @staticmethod
    def find_summon(summon: str) -> Optional[Tuple[int, int]]:
        """Find the location of the specified Summon.

        Returns:
            Coordinates of summon.
        """
   
        for _ in range(0,2):
            result = ImageUtils._match(
                            f"{ImageUtils._current_dir}/images/summons/{summon}.jpg")
            if result != None: return result
        return None
    
    @staticmethod
    def get_button_dimensions(image_name: str) -> Tuple[int, int]:
        """Get the dimensions of a image in /images/buttons/ folder.

        Args:
            image_name (str): File name of the image in /images/buttons/ folder.

        Returns:
            (Tuple[int, int]): Tuple of the width and the height of the image.
        """
        if Settings.custom_scale == 1.0:
            image = PIL.Image.open(f"{ImageUtils._current_dir}/images/buttons/{image_name}.jpg")
        else:
            image = PIL.Image.open(f"temp/rescaled.png")
        width, height = image.size
        image.close()
        return width, height

    @staticmethod
    def _play_captcha_sound() -> None:
        """Plays the CAPTCHA.mp3 music file.
        """
        playsound(f"{ImageUtils._current_dir}/backend/CAPTCHA.mp3", block = False)


    @staticmethod
    def generate_alert_for_captcha() -> None:
        """Displays a alert that will inform users that a CAPTCHA was detected.

        """
        ImageUtils._play_captcha_sound()
        pyautogui.alert(
            text = "Stopping bot. Please enter the CAPTCHA yourself and play this mission manually to its completion. \n\nIt is now highly recommended that you take a break of several hours and "
                   "in the future, please reduce the amount of hours that you use this program consecutively without breaks in between.",
            title = "CAPTCHA Detected!", button = "OK")

    @staticmethod
    def generate_alert(message: str) -> None:
        """Displays a alert that will inform users about various user errors that may occur.

        Args:
            message (str): The message to be displayed.
        """
        ImageUtils._play_captcha_sound()
        pyautogui.alert(text = message, title = "Exception Encountered", button = "OK")
