const Discord = require("discord.js");
const { parse } = require("twemoji-parser");
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
    name: "jumbo",
    aliases: ["e", "enlarge", "enlargen"],

    run: async (client, message, args) => {
        let user = message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.member;

        const emoji = args[0];
        if (!args[0]) {
            const enlargeEmbed = new Discord.MessageEmbed()
                .setAuthor(message.author.username, message.author.avatarURL({
                    dynamic: true
                }))
                .setTitle('Command: jumbo')
                .setDescription('Returns a large emoji or server emote')
                .addField('**Aliases**', 'e, enlarge, enlargen', true)
                .addField('**Parameters**', 'emoji, characters', true)
                .addField('**Information**', `N/A`, true)
                .addField('**Usage**', '\`\`\`Syntax: jumbo <emoji or emote>\nExample: jumbo 🔥\`\`\`')
                .setFooter(`Module: misc`)
                .setTimestamp()
                .setColor(color)
            if (!args[0]) return message.channel.send(enlargeEmbed)
        }
        let custom = Discord.Util.parseEmoji(emoji);
        const embed = new Discord.MessageEmbed()
            .setColor(user.displayHexColor || color);

        if (custom.id) {
            embed.setImage(`https://cdn.discordapp.com/emojis/${custom.id}.${custom.animated ? "gif" : "png"}`);
            return message.channel.send(embed);
        }
        else {
            let parsed = parse(emoji, { assetType: "png" });
            if (!parsed[0]) return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: You must input a **valid** emoji` } });

            embed.setImage(parsed[0].url);
            return message.channel.send(embed);
        }

    }
}