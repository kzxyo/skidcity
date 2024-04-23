const { MessageEmbed, Permissions } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: "seticon",
        aliases: ["editicon"],
        description: "Set the icon of the server.",
        syntax: "seticon <image>",
        example: "seticon meow.png",
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

        const icon = message.attachments.first();

        if (!icon.url.endsWith(".png") && !icon.url.endsWith(".jpg") && !icon.url.endsWith(".jpeg")) {
            return displayCommandInfo(module.exports, session, message);
        }

        try {
            await message.guild.setIcon(icon.url);
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
                    .setDescription(`${session.grant} ${message.author}: The icon has been set to **[this image](${icon.url})**`)
                    .setColor(session.green)
            ]
        });
    }
}