const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const urban = require('relevant-urban')

module.exports = class UrbanCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'urban',
            aliases: [`ud`],
            description: 'searches for a definition on urban dictionary',
            type: client.types.SEARCH,
            subcommands: ['urban'],
            usage: `urban [word]`
        });
    }

    async run(message, args, client) {
        if(!args.length) {
            return this.help(message)
        }
        let def;
        if (args.length) {
            const defs = await urban(args.join(' ')).catch(() => {})
            if(!defs) return this.send_error(message, 1, `No match found for **${args.join(' ')}** on urban dictionary`)
            if (defs.constructor.name === 'Array') {
                let total = Object.keys(defs).length

                if (!defs || !total) return this.send_error(message, 1, `No match found for **${args.join(' ')}** on urban dictionary`)

                def = defs[1]

            } else if (defs.constructor.name === 'Definition') {

                def = defs

            }
            const embed = new MessageEmbed()
                .setAuthor(`Urban Dictionary`, `https://files.catbox.moe/kkkxw3.png`, `https://www.urbandictionary.com/`)
                .setThumbnail("https://cdn.discordapp.com/attachments/739360499086524476/745639669836021841/UD_2.PNG")
                .setTitle(`Definition of ${defs.word}`)
                .setURL(defs.urbanURL)
                .addField(`Definition`, `${defs.definition}`)
                .addField('Example(s)', defs.example ? defs.example : 'N/A')
                .setColor(this.hex)
                .setFooter(`Submitted by ${defs.author} - ${defs.thumbsUp} upvotes, ${defs.thumbsDown} downvotes`)
                .setTimestamp()
            return message.channel.send({ embeds: [embed] })

        } else {
            const embed = new MessageEmbed()
                .setAuthor(`Urban Dictionary`, `https://files.catbox.moe/kkkxw3.png`, `https://www.urbandictionary.com/`)
                .setTitle("Something went wrong.")
                .setColor(this.hex)
             message.channel.send({ embeds: [embed] })
        }
    }
};