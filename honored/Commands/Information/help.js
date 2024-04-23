const { MessageEmbed } = require('discord.js');

async function displayCommandInfo(session, message, commandName) {
    let command;
    if (session.commands.has(commandName.toLowerCase())) {
        command = session.commands.get(commandName.toLowerCase());
    } else if (session.aliases.has(commandName.toLowerCase())) {
        const alias = session.aliases.get(commandName.toLowerCase());
        command = session.commands.get(alias);
    }

    if (!command) {
        const errorMessage = {
            color: session.warn,
            description: `${session.mark} ${message.author}: Invalid command. Use \`help\` to see the list of available commands.`,
        };
        return message.channel.send({ embeds: [errorMessage] });
    }

    const commandInfo = new MessageEmbed()
        .setColor(session.color)
        .setTitle(`Command: ${command.configuration.commandName}`)
        .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
        .setDescription(command.configuration.description || 'N/A')
        .addFields(
            { name: 'Permissions', value: command.configuration.permissions || 'N/A', inline: true },
            { name: 'Module', value: command.configuration.module || 'N/A', inline: true },
            { name: 'Parameters', value: command.configuration.parameters || 'N/A', inline: true },
        )
        .addField('Usage:', `\`\`\`Syntax: ${command.configuration.syntax || 'N/A'}\nExample: ${command.configuration.example || 'N/A'}\`\`\``)
        .setFooter(`Aliases: ${command.configuration.aliases.join(', ')}`);

    if (command.configuration.subcommands && command.configuration.subcommands.length > 0) {
        commandInfo.addField('Subcommands:', `${command.configuration.subcommands.join('\n')}`);
    }

    return message.channel.send({ embeds: [commandInfo] });
}


module.exports = {
    configuration: {
        commandName: 'help',
        aliases: ['commands', 'h', 'cmds'],
        description: 'Displays a list of available commands.',
        syntax: 'help [command]',
        example: 'help fortnite',
        permissions: 'N/A',
        parameters: 'command',
        module: 'information'
    },
    run: async (session, message, args) => {
        const commandName = args[0];
        if (commandName) {
            return displayCommandInfo(session, message, commandName);
        }
        message.channel.send({ content: `${message.author}: <https://honored.rip/help>, join the discord server @ https://honored.rip/discord` });
    }
};
