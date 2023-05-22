const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const fetch = require('node-fetch');

module.exports = class Banner extends Command {
    constructor(client) {
        super(client, {
            name: 'banner',
            usage: 'banner [user mention/ID]',
            description: 'Display a members banner',
            type: client.types.INFO,
            subcommands: ['banner @conspiracy']
        });
    }
    async run(message, args) {
        let banner
        const member = this.functions.get_member_or_self(message, args.join(' '))
        if(!member) return this.invalidUser(message)
        let response = fetch(`https://discord.com/api/v8/users/${member.id}`, {
            method: 'GET',
            headers: {
                Authorization: `Bot ${this.config.token}`
            }
        })
        
        response.then(a => {
            a.json().then(data => {
                let receive = data['banner']
                let response1 = fetch(`https://cdn.discordapp.com/banners/${member.id}/${receive}.gif`, {
                    method: 'GET',
                    headers: {
                        Authorization: `Bot ${this.config.token}`
                    }
                })
                response1.then(b => {
                    if (b.status == 415) {
                        banner = `https://cdn.discordapp.com/banners/${member.id}/${receive}.png?size=1024`
                    } else {
                        banner = `https://cdn.discordapp.com/banners/${member.id}/${receive}.gif?size=1024`
                    }
                    if(receive === null && data['banner_color'] !== null) banner =  `https://singlecolorimage.com/get/${data['banner_color'].replace('#', '')}/400x100`
                    else if(receive === null) return this.send_error(message, 1, `The user you provided doesnt have a banner`)
                    const embed = new MessageEmbed()
                        .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
                        .setTitle(`${member.user.username}'s banner`)
                        .setImage(banner)
                        .setColor(data['banner_color'] || this.hex)
                    message.channel.send({ embeds: [embed] })

                })
            })
        })
    }

}