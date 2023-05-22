const Command = require('../Command.js');
const Bearer = 'AAAAAAAAAAAAAAAAAAAAAGUsTgEAAAAAAM4rFHVRJVSKVhG9D7cky5Uo1Ts%3Dza92cCnc8O73L2TcrL1cQrl5NWntgqB1m29swOoVtPIkgpWqB7'

const request = require('node-superfetch');
const {
    MessageEmbed
} = require('discord.js');
module.exports = class Twit extends Command {
    constructor(client) {
        super(client, {
            name: 'twitter',
            aliases: ['tw', 'twit'],
            description: `Search for a twitter account`,
            subcommands: ['twitter [user]'],
            usage: `twitter [user]`,
            type: client.types.SEARCH
        });
    }
    async run(message, args) {
        const moment = require("moment")
        if (!args.length) return this.help(message)
        const name = args.join(' ')
        try{ 
        const {
            body
        } = await request.get("https://api.twitter.com/1.1/users/show.json")
            .set({
                Authorization: `bearer ${Bearer}`
            }).query({
                screen_name: name
            })
        const embed = new MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({
                dynamic: true
            }))
            .setColor(this.hex)
            .setTitle(`${body.name} (${body.screen_name}) ${body.verified ? `<:verified:859242659339042836>` : ''}`)
            .addField(`Tweets`, `${body.statuses_count}`, true)
            .addField(`Followers`, `${body.followers_count}`, true)
            .addField(`Following`, `${body.friends_count}`, true)
            .setThumbnail(body.profile_image_url)
            .setURL(`https://twitter.com/${encodeURIComponent(body.screen_name)}`)
            .setFooter(`Twitter - Created ${moment(body.created_at).format('YY/MM/DD')}`, 'https://1000logos.net/wp-content/uploads/2017/06/Twitter-Logo.png')
           if(body.description) embed.setDescription(`${body.description}`)
           message.channel.send({ embeds: [embed] })
        } catch(error) {
            return this.send_info(message, `There was an error searching for **[${name}](https://twitter.com/${name})** : ${error.text
            .replace(':', '')
            .replace('"errors"', '')
            .replace('{', '')
            .replace('[', '')
            .replace(']', '')
            .replace('}', '')}`)
           
        }
    }
};