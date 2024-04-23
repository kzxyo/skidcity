const { MessageEmbed, Permissions } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration : {
        commandName: "setbanner",
        aliases: ["editbanner"],
        description: "Set the banner of the server.",
        syntax: "setbanner <image>",
        example: "setbanner meow.png",
        permissions: "manage_guild",
        parameters: "image",
        module: "utility"
    },

    run: async(session, message, args) => {
        if (!message.member.permissions.has(Permissions.FLAGS.MANAGE_SERVER)) return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: You're **missing** permission: \`manage_server\``)
                    .setColor(session.warn)
            ]
        });

        if (!message.attachments.first()) {
            return displayCommandInfo(module.exports, session, message);
        }

        const banner = message.attachments.first();

        if (!banner.url.endsWith(".png") && !banner.url.endsWith(".jpg") && !banner.url.endsWith(".jpeg")) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setDescription(`${session.mark} ${message.author}: The image must be a **PNG, JPG, or JPEG** file.`)
                        .setColor(session.warn)
                ]
            });
        }

        try {
            await message.guild.setBanner(banner.url);
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
                    .setDescription(`${session.grant} ${message.author}: The banner has been set to **[this image](${banner.url})**`)
                    .setColor(session.green)
            ]
        });

    }
};