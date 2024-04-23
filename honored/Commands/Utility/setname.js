const { MessageEmbed, Permissions } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: "setname",
        aliases: ["editname"],
        description: "Set the name of the server.",
        syntax: "setname <name>",
        example: "setname Meow",
        permissions: "manage_guild",
        parameters: "name",
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

        if (!args[0]) {
            return displayCommandInfo(module.exports, session, message);
        }

        try {
            await message.guild.setName(args.join(" "));
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
                    .setDescription(`${session.grant} ${message.author}: The server name has been set to **${args.join(" ")}**`)
                    .setColor(session.green)
            ]
        });
    }
};