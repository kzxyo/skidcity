const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

module.exports = class ModerationHistory extends Command {
    constructor (Client) {
        super (Client, 'moderationhistory', {
            Aliases : [ 'modhistory', 'mhistory' ],

            Permissions : [ 'ManageMessages' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        try {
            const Member = Arguments[0] ? Message.mentions.members.first() || Message.guild.members.cache.get(Arguments[0]) || Message.guild.members.cache.find((Member) => Member.user.username.toLowerCase().includes(Arguments[0].toLowerCase()) || Member.user.tag.toLowerCase().includes(Arguments[0].toLowerCase()) || Member.displayName.toLowerCase().includes(Arguments[0].toLowerCase())) : Message.member
            
            if (!Member) { 
                return new Client.Response(
                    Message, `Couldn't find a **Member** with that username.`
                ) 
            }

            Client.Database.query(`SELECT * FROM history WHERE guild_id = ${Message.guild.id} AND moderator_id = ${Member.id}`).then(async ([Results]) => {
                if (Results.length === 0) {
                    return new Client.Response(
                        Message, `Couldn't find any recorded **Moderation Actions** for member **${Member.user.tag}**.`
                    )
                }

                Results = Results.filter((Case) => Case.moderator_id === Member.id)
                Results = Results.sort((a, b) => b.id - a.id)

                const Embeds = [], Entries = Results.Pager(3); var Index = 0

                for (const Entry of Entries) {
                    const Fields = []

                    Entry.map((Item) => {
                        if (Item.id) {
                            const User = Client.users.cache.get(Item.member_id)
                            const Channel = Client.channels.cache.get(Item.channel_id)

                            ++Index

                            Fields.push({
                                name : `Moderation Case **#${Item.id}** (${Item.action})`,
                                value : `<t:${Item.timestamp}:F>\n${Item.channel_id !== null ? `**Channel**: ${Channel ? Channel.name : 'Unknown Channel'} (*${Channel ? Channel.id : 'N/A'}*)` : `**Member**: ${User ? User.tag : 'Unknown User'} (*${User ? User.id : 'N/A'}*)`}\n**Reason**: ${Item.reason}`
                            })
                        }
                    })

                    Embeds.push(new EmbedBuilder({
                        author : {
                            name : `Moderation History for ${Member.user.tag}`,
                            iconURL : Member.user.displayAvatarURL({
                                dynamic : true
                            })
                        },
                        fields : Fields,
                        footer : {
                            text : `Page 1 out of 1`
                        }
                    }).setColor(Client.Color))
                }

                if (Embeds.length > 1) { 
                    const Paginator = new Client.Paginator(Message)
                    
                    Paginator.SetEmbeds(Embeds)
                    
                    await Paginator.Send()
                } else { 
                    return Message.channel.send({ 
                        embeds: [
                            Embeds[0]
                        ] 
                    }) 
                }
            })
        } catch (Error) {
            return new Client.Error(
                Message, 'moderationhistory', Error
            )
        }
    }
}