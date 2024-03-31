from typing import List, Tuple, Dict, Optional
from utils.message_log import MessageLog as Log
from utils.debugger import Debugger as Debug


class Parser:
    """
    Provides the utility functions for parsing combat script
    """

    @staticmethod
    def pre_parse(text: List[str]) -> List[str]:
        """ Remove all comment and empty line and lowercased result
        """
        result = []
        for line in [line.strip().lower() for line in text]:
            if line == "" or line.startswith("#") or line.startswith("/"):
                continue
            else:
                result.append(line.lstrip())
        return result

    @staticmethod
    def _parse_summon(txt: List[str]):
        if len(txt) == 0:
            return (txt, None)
        if not txt[0].startswith("summon:"):
            return (txt, None)
        return (txt[1:], txt[0].split(':')[1])

    @staticmethod
    def _parse_url(txt: List[str]):
        if len(txt) == 0:
            return (txt, None)
        if not txt[0].startswith("http"):
            return (txt, None)
        return (txt[1:], txt[0])

    @staticmethod
    def _parse_repeat(txt: str) -> int:
        if len(txt) == 0:
            return (txt, None)
        if not txt[0].startswith("repeat:"):
            return (txt, None)
        return (txt[1:], int(txt[0][-1]))

    @staticmethod
    def _parse_character(line: str, is_char_selected: bool) -> List[Tuple[str, Dict[str, int]]]:
        """ Parse a line of character action

        Returns:
            Same type as _parse_combact
        """
        ret = []
        is_skill_selected = False
        chains = line.split('.')
        char_idx = int(chains.pop(0)[-1])
        if char_idx not in (1, 2, 3, 4):
            raise ValueError(
                f"[Parser] Invalid chracter number: {char_idx}")
        if is_char_selected:
            ret += [{"changechar": {"idx": char_idx-1}}]
        else:
            ret += [{"selectchar": {"idx": char_idx-1}}]

        for cmd in chains:
            if cmd.startswith('useskill'):
                skill_idx = int(cmd[-2])
                if skill_idx not in (1, 2, 3, 4):
                    raise ValueError(
                        f"[Parser] Invalid skill number: {skill_idx}")
                ret += [{"useskill": {"idx": skill_idx-1}}]
                is_skill_selected = True
            elif cmd.startswith('target'):
                target_idx = int(cmd[-2])
                if target_idx not in (1, 2, 3, 4, 5, 6):
                    raise ValueError(
                        f"[Parser] Invalid skill target number: {target_idx}")
                if not is_skill_selected:
                    raise RuntimeError(
                        f"[Parser] Select a skill before picking a target")
                ret += [{'target': {"idx": target_idx-1}}]
                is_skill_selected = False
        return ret

    @staticmethod
    def parse_raids(txt: List[str]):
        """ Parse user script

        Returns:
            list of raid informations (url, summon, repeats) and combact action
        """
        remain_txt = Parser.pre_parse(txt)
        list_of_raids = {} # actually a json dict
        raid_cnt = 0
        raid_info = {}
        combact_actions = {}

        while len(remain_txt) > 0:

            lines_left = len(remain_txt)
            
            remain_txt, url = Parser._parse_url(remain_txt)
            if url is not None:
                # if a new url is parse, conclude the previous raid script
                if  raid_info.get('url') is not None:
                    raid_cnt += 1
                    list_of_raids[raid_cnt] = {'info': raid_info, 'combact_actions':combact_actions}
                    raid_info = {}
                    combact_actions = {}
                # at both case
                raid_info['url'] = url
            remain_txt, summon = Parser._parse_summon(remain_txt)
            if summon is not None: raid_info['summon'] = summon
            remain_txt, repeat = Parser._parse_repeat(remain_txt)
            if repeat is not None: raid_info['repeat'] = repeat
            remain_txt, combact_actions = Parser._parse_combact(remain_txt)

            # the line is unparsable, delete the line
            if lines_left == len(remain_txt):
                remain_txt.pop(0)
        # conclude the previous raid at the EOL
        raid_cnt += 1
        list_of_raids[raid_cnt] = {'info': raid_info, 'combact_actions':combact_actions}

        return list_of_raids
    
    @staticmethod
    def _parse_combact(text: List[str]):
        """Parse entire raid combact actions

        Returns:
            remaing text, actions
        """
        if len(text) == 0:
            return (text, {})
        
        remain_txt = text
        combact_actions = {}
        while len(remain_txt) != 0 and remain_txt[0].startswith('turn'):
            remain_txt, turns, actions = Parser._parse_turn(remain_txt)
            combact_actions[turns] = actions
        else:
            return (remain_txt, combact_actions)

    @staticmethod
    def _parse_turn(text: List[str]):
        """Parse the combact action

        Returns:
            remaing text, turns, actions
        """
        remain_txt = text
        turn = int(remain_txt.pop(0)[-2])

        is_char_selected: bool = False
        combact_act = []
        while len(remain_txt) > 0:
            line = remain_txt.pop(0)

            if line.startswith('character'):
                combact_act += Parser._parse_character(line, is_char_selected)
                is_char_selected = True
            
            elif line.startswith("wait"):
                combact_act += [{"wait": {"time": int(line[5:-1])}}]
            
            elif line.startswith("summon"):
                idx = int(line[-2])
                if idx not in (1,2,3,4,5,6):
                    raise ValueError
                if is_char_selected:
                    combact_act += [{"deselectchar", {}}]
                    is_char_selected = False
                combact_act += [{'usesummon': {'idx': idx-1}}]
            
            elif line == "attack":
                is_char_selected = False
                combact_act += [(line, {})]
            
            elif line == "enablefullauto":
                if is_char_selected:
                    combact_act += [{"deselectchar", {}}]
                    is_char_selected = False
                combact_act += [{line: {}}]
            
            elif line == 'end':
                break

            else:
                combact_act += [{line: {}}]

        return (remain_txt, turn, combact_act)