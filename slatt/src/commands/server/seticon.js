const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');

module.exports = class recenttracks extends Command {
    constructor(client) {
        super(client, {
            name: 'seticon',
            aliases: ['seti'],
            usage: 'setbanner [image | cdn link]',
            subcommands: ['seticon'],
            description: 'sets the Icon to your desired picture',
            clientPermissions: ['MANAGE_GUILD'],
            userPermissions: ['MANAGE_GUILD'],
            type: client.types.SERVER,
        });
    }
    async run(message, args) {
        let image
        if (message.attachments.first()) {
            image = message.attachments.first().url
        } else {
            if (!message.attachments.first()) image = args.join(' ')
            if(image && !image.startsWith('https://cdn.discordapp.com/')) { 
                return this.send_error(message, 1, `Your icon URL link must be a **cdn** type link`)
            }
        }
        await message.guild.setIcon(image).catch(error => {
            return this.send_error(message, 1, `There was an error updating your banner: ${error.name}`)
        })
        const embed = new MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({
                dynmic: true
            }))
            .setTitle(`Guild Icon Updated`)
            .setImage(image)
            .setFooter(message.guild.name, message.guild.iconURL({
                dynamic: true
            }))
            .setColor(this.hex)
        message.channel.send({ embeds: [embed] })
        message.client.utils.send_log_message(message, message.member, this.name, `**{user.tag}** Updated server icon to [icon](${message.guild.iconURL()})`)
    }
}