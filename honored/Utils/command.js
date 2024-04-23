const { MessageEmbed } = require('discord.js');

function displayCommandInfo(command, session, message) {
    const commandInfo = new MessageEmbed()
        .setColor(session.color)
        .setTitle(`Command: ${command.configuration.commandName}`)
        .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
        .setDescription(command.configuration.description || 'N/A')
        .addField('Usage:', `\`\`\`Syntax: ${command.configuration.syntax || 'N/A'}\nExample: ${command.configuration.example || 'N/A'}\`\`\``)

    if (command.configuration.subcommands && command.configuration.subcommands.length > 0) {
        commandInfo.addField('Subcommands:', `${command.configuration.subcommands.join('\n')}`);
    }

    return message.channel.send({ embeds: [commandInfo] });
}

module.exports = {
    displayCommandInfo
};
