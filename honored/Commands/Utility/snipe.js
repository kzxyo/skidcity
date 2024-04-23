const moment = require("moment");
const { MessageEmbed } = require("discord.js");

module.exports = {
    configuration: {
        commandName: 'snipe',
        description: 'Snipe a recently deleted message',
        aliases: ["s"],
        syntax: 'snipe',
        example: 'snipe',
        permissions: 'N/A',
        parameters: 'N/A',
        module: 'utility'
    },
    run: async (session, message, args) => {
        try {
            const snipes = session.snipes.get(message.channel.id);

            if (!snipes || snipes.length === 0) {
                const errorEmbed = new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: There is nothing to snipe`);
                return await message.channel.send({ embeds: [errorEmbed] });
            }

            const latestSnipe = snipes[0];

            const { msg, time, image } = latestSnipe;

            if (!msg || !msg.author) {
                throw new Error('Message or author not found');
            }

            const username = msg.author.username;
            const avatar = msg.author.displayAvatarURL({ dynamic: true });

            const embed = new MessageEmbed()
                .setAuthor(`${username}`, avatar)
                .setDescription(`${msg.content}`)
                .setImage(image)
                .setColor(session.color)
                .setFooter(`Deleted ${moment(time).fromNow()}`);

            if (msg.attachments.size > 0) {
                const attachments = msg.attachments.map((attachment) => attachment.url).join("\n");
                embed.addField("Attachments", attachments);
            }

            await message.channel.send({ embeds: [embed] });
        } catch (error) {
            console.error('Error while sniping:', error);
        }
    }
};
