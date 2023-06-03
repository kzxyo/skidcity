module.exports.runEvent = async (client, interaction, currentDate) => {
    const { MessageEmbed } = require('discord.js');
    if (interaction.type !== "APPLICATION_COMMAND") return
        interaction.reply({ embeds: [new MessageEmbed()
            .setColor("#FFFFFF")
            .setTitle("Please Wait <a:vile_loading:1045004235915411536>")
            .setDescription("Running the command you've requested.")
            .setTimestamp()
            .setFooter({
                text: `${client.user.username}`,
                iconURL: client.user.displayAvatarURL()
            })], ephemeral: false})
    var message = await interaction.fetchReply()
    var generalData = {
        message: message,
        msg_id: message.id,
        channel_id: interaction.channelId,
        guild_id: interaction.guildId,
        user_id: interaction.user.id,
        username: interaction.user.username,
        tag: interaction.user.discriminator,
        fullUser: `${interaction.user.username}#${interaction.user.discriminator}`,
        joinedTS: interaction.member.joinedTimestamp,
        premiumTS: interaction.member.premiumSinceTimestamp,
        currentDate: currentDate
    }
    if (client.slash.get(interaction.commandName.toString().toLowerCase()) === undefined || client.slash.get(interaction.commandName.toString().toLowerCase()) === null) await message.reply({ embeds: [new MessageEmbed()
        .setColor("#8B0000")
        .setAuthor({ name: "An Error Occured" })
        .setTitle("Command Not Found")
        .setDescription(`The command ${interaction.commandName.toString().toLowerCase()} was not found or has not been registered on this bot.`)
        .setTimestamp()
        .setFooter({
            text: `${client.user.username}`,
            iconURL: client.user.displayAvatarURL()
        })], ephemeral: true })
        var cmd = client.slash.get(interaction.commandName.toString().toLowerCase())
        cmd.runCmd(client, interaction, generalData)
}