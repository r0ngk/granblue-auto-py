from utils.parser import Parser

case = [
    [    "// This script starts Semi-Auto mode on Turn 1.",
            "// It will go uninterrupted until either the party wipes or the quest/raid ends.",
            "",
            "",
            "https://game.granbluefantasy.jp/#quest/supporter/800021/22",
            "summon:Kaguya",
            "repeat:1",
            "",
            "Turn 1:",
            "   quickSummon",
            "   subBack",
            "End",
            "",
            "https://game.granbluefantasy.jp/#quest/supporter/800021/22",
            "suRmmon:Kaguya",
            "",
            "Turn 5:",
                "quickSummon",
                "character1.useSkill(2).useSkill(4)",
                "subBack",
            "End",
            ]
]
result = [
    {1: {'info': {'url': 'https://game.granbluefantasy.jp/#quest/supporter/800021/22', 'summon': 'kaguya', 'repeat': 1}, 'combact_actions': {1: [{'quicksummon': {}}, {'subback': {}}]}}, 2: {'info': {'url': 'https://game.granbluefantasy.jp/#quest/supporter/800021/22'}, 'combact_actions': {5: [{'quicksummon': {}}, {'selectchar': {'idx': 0}}, {'useskill': {'idx': 1}}, {'useskill': {'idx': 3}}, {'subback': {}}]}}}
]

for i in range(0, len(case)):
    if Parser.parse_raids(case[i]) == result[i]:
        print(f"test {i} PASS")
    else:
        print(f"test {i} FAIL")

