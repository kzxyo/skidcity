const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const ReactionMenu = require('../ReactionMenu.js');
const {
    default: axios
} = require('axios');
module.exports = class ImageCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'image',
            usage: 'image [query]',
            aliases: ['img'],
            subcommands: ['image'],
            description: 'searches for an image',
            type: client.types.SEARCH,
        });
    }

    async run(message, args) {
        message.channel.sendTyping()
   
        let query = args.join(' ')
        if(!query) return this.help(message)
        let googKey = "AIzaSyDHcNBPqv-GpTR6_oyA6EnTyiRXeGUjokI";
        let cxKey = "b7498d486b2d19b97";
        let page = 1;
        const url = `https://www.googleapis.com/customsearch/v1?key=${googKey}&cx=${cxKey}&q=${query}&searchType=image${message.channel.nsfw ? '' : '&safe=active'}&alt=json&start=${page}`
        axios(url).then(res => {
            let n = 0
            const images = res.data.items
            if(!images) {
                return this.send_error(message, 1, `There was no result on google for **${query}**`)
            }
            const embed = new MessageEmbed()
                .setAuthor(`(${images[n].displayLink})`)
                .setTitle(images[n].title)
                .setURL(images[n].link)
                .setDescription(images[n].snippet)
                .setImage(images[n].link)
                .setFooter(`Google Images · ${n+1}/${images.length}`, 'https://cdn.discordapp.com/attachments/780547065712345088/830728785199497256/google_logo1600.png')
                .setColor(this.hex)
            const json = embed.toJSON();
            const previous = () => {
                (n <= 0) ? n = images.length - 1: n--;
                return new MessageEmbed(json)
                    .setAuthor(`(${images[n].displayLink})`)
                    .setTitle(images[n].title.slice(0, 300) + '...')
                    .setURL(images[n].link)
                    .setDescription(images[n].snippet.slice(0, 300) + '...')
                    .setImage(images[n].link)
                    .setFooter(`Google Images · ${n+1}/${images.length}`, 'https://cdn.discordapp.com/attachments/780547065712345088/830728785199497256/google_logo1600.png')
                    .setColor(this.hex)
            };
            const next = () => {
                (n >= images.length - 1) ? n = 0: n++;
                return new MessageEmbed(json)
                    .setAuthor(`(${images[n].displayLink})`)
                    .setTitle(images[n].title)
                    .setDescription(images[n].snippet)
                    .setImage(images[n].link)
                    .setFooter(`Google Images · ${n+1}/${images.length}`, 'https://cdn.discordapp.com/attachments/780547065712345088/830728785199497256/google_logo1600.png')
                    .setColor(this.hex)
            };

            const reactions = {
                'LEFT_ARROW': previous,
                'STOP': null,
                'RIGHT_ARROW': next,
            };

            const menu = new ReactionMenu(
                message.client,
                message.channel,
                message.member,
                embed,
                null,
                null,
                reactions,
                180000
            );
            menu.reactions['STOP'] = menu.stop.bind(menu);
        })


    }
}
