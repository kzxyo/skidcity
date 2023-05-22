import discord, os, sys, asyncio, aiohttp, subprocess, datetime, textwrap, copy, pathlib, typing, traceback, json, time, random, humanize
from discord.ext import tasks, commands
from datetime import datetime, timedelta, timezone
from pathlib import Path

import collections
import typing


class UwU:
    def __init__(self, result=""):
        self.result = result
        self.alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")

    def convert(self, word):
        converted = ""
        doubleT = doubleT_Presence = th_Presence = False

        for i in range(len(word)):
            if doubleT or th_Presence:
                doubleT = th_Presence = False
                continue
            elif (word[i].lower() == "l" and not doubleT_Presence) or (
                word[i].lower() == "r"
            ):
                converted += "W" if word[i].isupper() else "w"
            elif (word[i].lower() == "t") and (
                (word[i + (1 if i + 1 < len(word) else 0)].lower() == "t")
            ):
                converted += (
                    (
                        ("D" if word[i].isupper() else "d")
                        + ("D" if word[i + 1].isupper() else "d")
                    )
                    if i + 1 < len(word)
                    else "t"
                )
                doubleT = doubleT_Presence = True if i + 1 < len(word) else False
            elif (word[i].lower() == "t") and (
                (word[i + (1 if i + 1 < len(word) else 0)].lower() == "h")
            ):
                converted += (
                    ("F" if word[i].isupper() else "f") if i + 2 == len(word) else "t"
                )
                th_Presence = True if i + 2 == len(word) else False
            else:
                converted += word[i]
        if len(word) > 0 and (word[0] != ":" or word[-1] != ":"):
            self.result += (
                (converted[0] + "-" + converted[0:])
                if (random.randint(1, 10) == 1 and converted[0] in self.alphabet)
                else converted
            ) + ""
        else:
            self.result += word + " "

        return self.result


def send_uwu(sentence):

    x = UwU()
    for word in sentence:
        x.convert(word)

    return x.result
