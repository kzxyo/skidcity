const moment = require("moment");
const { MessageEmbed } = require("discord.js");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
const pagination = require("/root/rewrite/Utils/paginator.js");
const { default: axios } = require('axios');

module.exports = {
    configuration: {
        commandName: 'image',
        description: 'Search google for images',
        aliases: ["img"],
        syntax: 'image [query]',
        example: 'image cat',
        permissions: 'N/A',
        parameters: 'query',
        module: 'utility'
    },
    run: async (session, message, args) => {
        let query = args.join(' ')
        if (!query) return displayCommandInfo(module.exports, session, message);
        let googKey = "AIzaSyDHcNBPqv-GpTR6_oyA6EnTyiRXeGUjokI";
        let cxKey = "b7498d486b2d19b97";
        let page = 1;
        const url = `https://www.googleapis.com/customsearch/v1?key=${googKey}&cx=${cxKey}&q=${query}&searchType=image${message.channel.nsfw ? '' : '&safe=active'}&alt=json&start=${page}`
        axios(url).then(res => {
            let n = 0
            const images = res.data.items
            if (!images) {
                return message.channel.send({ embeds: [new MessageEmbed().setDescription(`${session.mark} ${message.author}: There are no results for **${query}**`).setColor(session.warn)] })
            }
            const embeds = images.slice(0, 10).map(image => (
                new MessageEmbed()
                    .setAuthor(message.author.username, message.author.displayAvatarURL({ dynamic: true }))
                    .setImage(image.link)
                    .setURL(image.link)
                    .setTitle(image.title)
                    .setColor(session.color)
            ));

            pagination(session, message, embeds, 10);
        })

    }
}
