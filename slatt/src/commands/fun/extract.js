const Command = require('../Command.js');
const { MessageEmbed } = require('discord.js');
const fetch = require('node-fetch');

module.exports = class Extract extends Command {
    constructor(client) {
        super(client, {
            name: 'extract',
            aliases: ['colorpicker', 'extractcolor', 'dominantcolor'],
            usage: 'extract <image | attachment>',
            description: 'Extract the most dominant color from an image',
            type: client.types.FUN
        });
    }
    async run(message, args) {
        if (!args.length && !message.attachments.first()) return this.help(message)
        let image
        if (message.attachments.first()) {
            image = message.attachments.first().url
        } else {
            if (!message.attachments.first()) image = args.join(' ')
        }
        image = image.replace('.webp', '').replace('.gif', '').replace('?size=512', '').replace('?size=1024', '').replace('.png', '').replace('.jpg', '') + '.png'
        const color = await message.client.utils.extract_color(image)
        fetch(`http://www.thecolorapi.com/id?hex=${color.replace('#', '')}`).then(response => response.json()).then(res => {
            if (!res || !res.hex) {
                return this.api_error(message, `Color`, `the color you provided was invalid`)
            }
            const embed = new MessageEmbed()
                .setAuthor(`Extracted color`)
                .setTitle(`${res.hex.value} (${res.hex.clean})`)
                .setDescription(`Name: ${res.name.value}`)
                .addField(`RGB`, `red: ${res.rgb.r}\ngreen: ${res.rgb.g}\nblue: ${res.rgb.b}`, false)
                .setColor(res.hex.value)
                .setImage(`https://singlecolorimage.com/get/${res.hex.clean}/400x100`)
                .setThumbnail(`https://via.placeholder.com/250x219/${res.hex.clean}/FFFFFF?text=%20`)
            message.channel.send({ embeds: [embed] })
        }).catch(e => {
            return this.api_error(message, `Color`, `${e}`)
        })
    }
};