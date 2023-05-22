const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
var fetch = require('node-fetch');

module.exports = class Instagram extends Command {
    constructor(client) {
        super(client, {
            name: 'instagram',
            aliases: ['insta', 'ig'],
            description: `View any profile on instagram`,
            subcommands: ['instagram [user]', 'instagram posts [user]'],
            type: client.types.SEARCH
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)

        const cookies = [
            "29901784935%3A6nBEr9GnyzcLnm%3A23"
        ]
        const sessionID = message.client.utils.rotate(cookies)
        const is_subcommand = message.client.subcommands.get(`instagram ${args[0]}`) || message.client.subcommand_aliases.get(`instagram ${args[0]}`)
        if (is_subcommand) return
        let name
        name = args.join(' ')
        const response = await fetch(`https://www.instagram.com/${name}/?__a=1`, {
            headers: {
                'cookie': `sessionid=${sessionID}; rur=ATN`
            }
        })
        const data = await response.json()
        if (!data.graphql) {
            return this.api_error(message, `instagram`, `Instagram returned no data for **[${name}](https://instagram.com/${encodeURIComponent(name)})**`)
        }
        
        const info = data.graphql.user
        const embed = new MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({
                dynamic: true
            }))
            .setTitle(`${info.username} ${info.full_name ? `(${info.full_name})` : ''} ${info.is_verified ? `<:verified:859242659339042836>` : ''}`)
            .setURL(`https://instagram.com/${encodeURIComponent(info.username)}`)
            .setDescription(`${info.biography || 'No bio yet'}`)
            .addField(`Followers`, info.edge_followed_by.count.toString(), true)
            .addField(`Following`, info.edge_follow.count.toString(), true)
            .addField(`Posts Count`, info.edge_owner_to_timeline_media.count.toString(), true)
            .setThumbnail(info.profile_pic_url_hd)
            .setColor(this.hex)
            .setFooter('Instagram', 'https://kmrealtyva.com/wp-content/uploads/2018/12/instagram-Logo-PNG-Transparent-Background-download.png')
        message.channel.send({ embeds: [embed] })
    }
};