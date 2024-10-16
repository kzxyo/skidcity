const { Message, Client } = require("discord.js");

module.exports = {
    name: "say",
    description: "Say a message",
    aliases: ["echo"],
    /**
     *
     * @param {Client} client
     * @param {Message} message
     * @param {String[]} args
     */
    run: async (client, message, args) => {
        const text = args.join(" ") || args[0]
        if(!text) return message.channel.send(`No text provided`)
        await message.channel.send(text)
    },
};