const malScraper = require('mal-scraper')
const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const { stripIndent } = require('common-tags');
const ReactionMenu = require('../ReactionMenu.js')
module.exports = class Anime extends Command {
    constructor(client) {
        super(client, {
            name: 'anime',
            usage: `anime <name>`,
            aliases: ["anilist"],
            description: `Fetch anime's from AniList`,
            type: client.types.SEARCH,
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        const anime = args.join(' ')

        const res = await malScraper.getResultsFromSearch(anime)
        if(!res || !res.length) return this.api_error(message, `Anime List`, `Could not find given anime`)
        let n = 0
        const embed = new MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({dynamic:true}))
            .setTitle(res[n].name)
            .setURL(res[n].url)
            .setDescription(stripIndent`
            **Created** ${res[n].payload.start_year}
            **Aired** ${res[n].payload.aired}
            **Score** ${res[n].payload.score}
            **Status** ${res[n].payload.status}
            `)
            .setImage(res[n].thumbnail_url)
            .setFooter(`ID: ${res[n].id} - Page ${n+1}/${res.length}`)
            .setColor(this.hex)
        const json = embed.toJSON();
        const previous = () => {
            (n <= 0) ? n = res.length - 1 : n--;
            return new MessageEmbed(json)
            .setAuthor(message.author.tag, message.author.avatarURL({dynamic:true}))
            .setTitle(res[n].name)
            .setURL(res[n].url)
            .setDescription(stripIndent`
            **Created** ${res[n].payload.start_year}
            **Aired** ${res[n].payload.aired}
            **Score** ${res[n].payload.score}
            **Status** ${res[n].payload.status}
            `)
            .setImage(res[n].image_url)
            .setFooter(`ID: ${res[n].id} - Page ${n+1}/${res.length}`)
            .setColor(this.hex)
        };
        const next = () => {
            (n >= res.length - 1) ? n = 0 : n++;
            return new MessageEmbed(json)
            .setAuthor(message.author.tag, message.author.avatarURL({dynamic:true}))
            .setTitle(res[n].name)
            .setURL(res[n].url)
            .setDescription(stripIndent`
            **Created** ${res[n].payload.start_year}
            **Aired** ${res[n].payload.aired}
            **Score** ${res[n].payload.score}
            **Status** ${res[n].payload.status}
            `)
            .setImage(res[n].image_url)
            .setFooter(`ID: ${res[n].id} - Page ${n+1}/${res.length}`)
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

    }
}