const { Message, MessageButton, MessageActionRow, MessageEmbed} = require("discord.js");

const pagination = async (session, message, embeds) => {

    const row = new MessageActionRow().addComponents(

        new MessageButton().setCustomId("prev").setEmoji(session.previous).setStyle("PRIMARY"),
        new MessageButton().setCustomId("next").setEmoji(session.next).setStyle("PRIMARY"),
        new MessageButton().setCustomId("skip").setEmoji(session.skip).setStyle("SECONDARY"),
        new MessageButton().setCustomId("cancel").setEmoji(session.cancel).setStyle("DANGER"),

    );
    let msg = await message.channel.send({
        embeds: [embeds[0]],
        components: [row],
    });
    const filter = async (i) => {
        await i.deferUpdate();

        if (i.user.id != message.author.id) {
            const notownerEmbed = new MessageEmbed()
                .setDescription(`${session.mark} ${message.author}: You are not the author of this embed`)
                .setColor(session.warn)
            await i.followUp({
                embeds: [notownerEmbed],
                ephemeral: true
            });
        }

        return i.user.id == message.author.id;
    };

    const collector = msg.createMessageComponentCollector({
        filter,
        time: 100000,
    });

    let index = 0;
    let cancelStatus = false;

    collector.on("collect", async (interaction) => {
        if (interaction.user.id != message.author.id) return;
        if (interaction.customId == "start") {
            index = 0;

            await msg.edit({
                embeds: [embeds[index]],
            });
        } else if (interaction.customId == "prev") {
            index = index > 0 ? --index : embeds.length - 1;

            await msg.edit({
                embeds: [embeds[index]],
            });
        } else if (interaction.customId == "next") {
            index = index + 1 < embeds.length ? ++index : 0;


            await msg.edit({
                embeds: [embeds[index]],
            });
        } else if (interaction.customId == "last") {
            index = embeds.length - 1;


            await msg.edit({
                embeds: [embeds[index]],
            });
        } else if (interaction.customId == "skip") {
            row.components.forEach((compo) => {
                compo.setDisabled(true);
            });
            msg.edit({ components: [row] })
            const skipEmbed = new MessageEmbed()
                .setDescription(`:1234: What **page** would you like to skip to?`)
                .setColor('#678dd5')
            await interaction.followUp({
                embeds: [skipEmbed],
                ephemeral: true,
            });
            const filter2 = (m) => {
                return m.author.id == message.author.id;
            };

            const collect = msg.channel.createMessageCollector({
                filter: filter2,
                time: 10000,
                max: 1,
            });

            collect.on("collect", async (m) => {
                if (isNaN(m.content)) {
                    collect.stop();
                    const passEmbed = new MessageEmbed()
                        .setDescription(` You can only pass **numbers**!`)
                        .setColor(colors.warn)
                    m.delete()
                    return await interaction.followUp({
                        embeds: [passEmbed],
                        ephemeral: true,
                    });
                } else {

                    const number = parseInt(m.content);
                    index = number - 1;
                    await m.delete();

                    await msg.edit({
                        embeds: [embeds[index]]
                    });

                }
            });
            collect.on("end", async () => {
                row.components.forEach((compo) => {
                    compo.setDisabled(false);
                });
                msg.edit({ components: [row] })
            });
        } else if (interaction.customId == "cancel") {
            cancelStatus = true;
            collector.stop();
            msg.delete()
        }
    });

    collector.on("end", async () => {
        if (cancelStatus) {
            return
        } else {
            return await msg.edit({
                components: [],
            });
        }
    });
};

module.exports = pagination;