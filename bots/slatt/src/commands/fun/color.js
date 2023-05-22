const Command = require('../Command.js');
const fetch = require('node-fetch');
const { MessageEmbed } = require('discord.js');
module.exports = class Color extends Command {
    constructor(client) {
        super(client, {
            name: 'color',
            aliases: ['hex', 'hexcode', 'hexcolor', 'tint'],
            description: `View information on a give color`,
            type: client.types.FUN,
            usage: `color [hexcode]`,
        });

    }

    async run(message, args) {
        let color
        let which
        const member = this.functions.get_member(message, args.join(' '))
        const role = this.functions.get_role(message, args.join(' '))
        if(!args[0]) {
            color = message.member.roles.highest.hexColor.toString() 
            which = 'your highest role'
        } else if (args[0] && args[0].toLowerCase() === 'random') {
            color = ("000000" + Math.random().toString(16).slice(2, 8).toUpperCase()).slice(-6)
            which = 'random'
         } else if (member) {
            color = member.roles.highest.color.toString()
            which = `member ${member.user.tag}`
        } else if (role) {
            color = role.hexColor.toString() || '000000'
            which = `role ${role.name}`
        } else {
            color = args[0] || '000000'
            which = `hex code: ${color}`
        }
        fetch(`http://www.thecolorapi.com/id?hex=${color.replace('#', '')}`).then(response => response.json()).then(res => {
            if (!res || !res.hex) {
                return this.api_error(message, `Color`, `the color you provided was invalid`)
            }
            const embed = new MessageEmbed()
                .setTitle(`${res.hex.value} (${res.hex.clean})`)
                .setDescription(`Name: ${res.name.value}`)
                .addField(`RGB`, `red: ${res.rgb.r}\ngreen: ${res.rgb.g}\nblue: ${res.rgb.b}`, false)
                .setColor(res.hex.value)
                .setFooter(`Viewing color for ${which}`)
                .setImage(`https://singlecolorimage.com/get/${res.hex.clean}/400x100`)
                .setThumbnail(`https://via.placeholder.com/250x219/${res.hex.clean}/FFFFFF?text=%20`)
            message.channel.send({ embeds: [embed] })
        }).catch(e => {
            return this.api_error(message, `Color`, `${e}`)
        })
    }
}