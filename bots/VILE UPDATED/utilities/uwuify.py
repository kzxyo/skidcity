import re, random
from enum import IntFlag
from typing import Union


class UwuifyFlag(IntFlag):
    SMILEY = 1
    YU = 2
    STUTTER = 4

    
SMILEYS = [
    '>_<',
    'uwu',
    'owo',
]

UWU = str.maketrans({'r': 'w', 'l': 'w', 'R': 'W', 'L': 'W'})

YU = str.maketrans({'u': 'yu', 'U': 'yU'})

ER_REPLACE = re.compile(r'(\b\w{2,})er\b', re.IGNORECASE)


def _do_yu(entry: str) -> str:
    
    final = list()
    for word in entry.split():
        if word:
            final.append(word[0] + word[1:].translate(YU))
        else:
            final.append(' ')
            
    return ' '.join(final)


def _do_uwu(entry: str) -> str:
    regexed = ER_REPLACE.sub(r'\g<1>a', entry)
    translated = regexed.translate(UWU)
    return translated


def _do_smiley(entry: str) -> str:
    
    if not isinstance(entry, list):
        entry = entry.split()

    final = list()
    for word in entry:
        if word.endswith(('.', '?', '!')):
            final.append(f'{word} {random.choice(SMILEYS)}')
        else:
            final.append(word)

    return ' '.join(final)


def _do_stutter(entry: str, stutter_every_nth_word: int = 4) -> str:
    
    listofstr = entry.split()
    result = list()
    
    for index, word in enumerate(listofstr):
        if index % stutter_every_nth_word == 0:
            result.append('{}-{}{}'.format(word[0], word[0], word[1:]))
        else:
            result.append(word)
            
    return ' '.join(result)


def uwuify(entry: Union[list, str], *, flags: UwuifyFlag = 0) -> str:
    
    if len(entry) == 0:
        return entry

    if flags & UwuifyFlag.YU:
        entry = _do_yu(entry)

    entry = _do_uwu(entry)

    if flags & UwuifyFlag.STUTTER:
        entry = _do_stutter(entry)

    if flags & UwuifyFlag.SMILEY:
        entry = _do_smiley(entry)

    return entry
