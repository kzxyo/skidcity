from modules import utils


def prefix(bot, message):

    try:
        x = utils.read_json("prefixes")[str(message.author.id)]["prefix"]
        return x

    except:
        try:
            x = utils.read_json("guildprefixes")[str(message.guild.id)]["prefix"]
            return x
        except:
            return utils.read_json("config")["prefix"]
