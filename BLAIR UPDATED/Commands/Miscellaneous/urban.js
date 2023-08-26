const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const { fetch } = require('undici'), qs = require('qs')

module.exports = class Urban extends Command {
    constructor (bot) {
        super (bot, 'urban', {
            description : 'Search for definitions on Urban Dictionary',
            parameters : [ 'query' ],
            syntax : '(query)',
            example : 'Amiri',
            aliases : [ 'urbandictionary', 'ud' ],
            module : 'Miscellaneous'
        })
    }

    async execute (bot, message, args, prefix) {
        try {
            if (!args[0]) {
                return bot.help(
                    message, this, prefix
                )
            }

            const query = qs.stringify({
                term : args.join(' ')
            })

            const definitions = await fetch(`https://api.urbandictionary.com/v0/define?${query}`, {
                method : 'GET'
            }).then((response) => response.json()).catch((error) => {
                return bot.warn(
                    message, `Bad response (\`${error.response.status}\`) from the **API**`
                )
            })

            if (!definitions.list.length) {
                return bot.warn(
                    message, `Couldn't find any definitions for **${args.join(' ')}**`
                )
            }

            const embeds = await Promise.all(
                definitions.list.map((definition) => {
                    const match = (text) => {
                        return text.replace(/\[(.+?)\]/g, (match, p1) => {
                            return `[${p1}](http://urbandictionary.com/define.php?${qs.stringify({ term : p1 })})`
                        })
                    }
    
                    definition.definition = match(definition.definition)
                    definition.example = match(definition.example)

                    return new Discord.EmbedBuilder({
                        author : {
                            name : message.member.displayName,
                            iconURL : message.member.displayAvatarURL({
                                dynamic : true
                            })
                        },
                        title : definition.word,
                        url : definition.permalink,
                        description : definition.definition,
                        fields : [
                            {
                                name : 'Example',
                                value : definition.example
                            }
                        ],
                        footer : {
                            context : `👍  ${parseInt(definition.thumbs_up).toLocaleString()} 👎  ${parseInt(definition.thumbs_down).toLocaleString()} - ${definition.author.length ? definition.author : 'N/A'}`
                        }
                    }).setColor(bot.colors.neutral)
                })
            )

            await new bot.paginator(
                message, {
                    embeds : embeds,
                    text : `{context} ∙ Page {page} of {pages}`
                }
            ).construct()
        } catch (error) {
            return bot.error(
                message, 'urban', error
            )
        }
    }
}