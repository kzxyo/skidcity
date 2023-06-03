const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');

module.exports = class PresenceCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'status',
            aliases: ['presence', 'bio'],
            usage: 'status [user]',
            description: 'Fetches a user\'s status',
            type: client.types.INFO,
            subcommands: ['status @conspiracy']
        });
    }
    async run(message, args) {
        const member = this.functions.get_member_or_self(message, args.join(' '))
        if (!member) return this.invalidUser(message)
        if (!member.presence || member.presence.status === 'offline') {
            return this.send_error(message, 1, `i could not find ${member}'s status. they are offline`)
        }
        const activities = []
        for (const activity of member.presence.activities.values()) {

            switch (activity.type) {
                case 'PLAYING':
                    activities.push(`• 🎮 Playing **${activity.name}** \`${activity.details}\` | **${activity.state}**`);
                    break;
                case 'LISTENING':
                    let trackURL = `https://open.spotify.com/track/${activity.syncID}`;
                    if (member.user.bot) activities.push(`• Listening to **${activity.name}**`);
                    else activities.push(`• <:spotify:827676144622764073> Listening to **[${activity.details}](${trackURL})** by **${activity.state}**`);
                    break;
                case 'WATCHING':
                    activities.push(`• :tv: Watching **${activity.name}**`);
                    break;
                case 'STREAMING':
                    activities.push(`• <:twitch:827675731793281044> Streaming **${activity.name}**`);
                    break;
                case 'CUSTOM':
                    activities.push(`${activity.emoji || ''} **${activity.state || 'No Status'}**`);
                    break;
            }
        }
        const embed = new MessageEmbed()
            .setAuthor(member.displayName, member.user.displayAvatarURL({
                dynamic: true
            }))
            .setColor(this.hex)
        if (member.presence.clientStatus) embed.setFooter(`mobile: ${member.presence.clientStatus.mobile || 'false'} | desktop: ${member.presence.clientStatus.desktop || 'false'} | web: ${member.presence.clientStatus.web || 'false'}`)
        if (activities.length) embed.setDescription(`${activities.join('\n')}`)
        return message.channel.send({ embeds: [embed] })
    }
}