import os
import discord
import html
import requests
import json
import time

# @brief Formats the translated text. At the moment, it only removes escape character codes
# @param text  The text to format
# @return The formatted text
def format(text):
    text = html.unescape(text)
    return text

# @brief Translates a string into the target language
# @param target  The target language. Must be a language code compatible with the Google Clould Translation API
#        text    The string to translate
# @return An embed with the translated text or an error message
def translate(target, text):
    # If no key was provided, return early
    key = os.environ["GOOGLE_KEY"]
    if(key == ""):
        return print("translator errored: no api key")

    # Split the text into lines
    lines = text.split("\n")

    # Generate the URL from the API key, and the target and source language.
    url = "https://translation.googleapis.com/language/translate/v2?key={k}&target={t}".format(k = key, t = target)
    # Add the lines to translate
    for line in lines:
        url += "&q={q}".format(q = line)

    # Call the API and convert the JSON received to a Python dictionnary
    response = json.loads(requests.post(url).text)

    # If there was an error, log it and return an error message
    if "error" in response:
        # Log the response
        timestamp = time.time()
        print(f"translator error: {response}")

        # Return an error embed
        return print("translator errored")

    # If the text was successfully translated
    elif "data" in response:
        # Store the translation in one string
        translation = ""
        for data in response["data"]["translations"]:
            translation += data["translatedText"]
            translation += "\n"

        # Format the text
        translation = format(translation)

        # Store it in an embed
        embed = discord.Embed(title = "Translation", type = "rich")
        embed.description = translation
        return translation