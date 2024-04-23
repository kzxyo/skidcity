const { MessageEmbed, Permissions } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: "setsplash",
        aliases: ["editsplash"],
        description: "Set the splash of the server.",
        syntax: "setsplash <image>",
        example: "setsplash meow.png",
        permissions: "manage_guild",
        parameters: "image",
        module: "utility"
    },

    run: async (session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_GUILD)) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_guild\``)
                    .setColor(session.warn)
            ]
        });

        if (!message.attachments.first()) {
            return displayCommandInfo(module.exports, session, message);
        }

        const splash = message.attachments.first();

        if (!splash.url.endsWith(".png") && !splash.url.endsWith(".jpg") && !splash.url.endsWith(".jpeg")) {
            return displayCommandInfo(module.exports, session, message);
        }

        try {
            await message.guild.setSplash(splash.url);
        } catch (error) {
            session.log("Error:", error);
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: An error occured, please contact support`)
                        .setColor(session.warn)
                ]
            });
        }

        return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.grant} ${message.author}: The splash has been set to **[this image](${splash.url})**`)
                    .setColor(session.green)
            ]
        });
    }
};