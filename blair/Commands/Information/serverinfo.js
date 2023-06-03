const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

module.exports = class ServerInfo extends Command {
    constructor (Client) {
        super (Client, 'serverinfo', {
            Aliases : [ 'si', 'guildinfo', 'gi' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        const UppercaseWords = String => String.replace(/^(.)|\s+(.)/g, Character => Character.toUpperCase())
        
        try {
            if (Arguments[0] && isNaN(Arguments[0])) {
                return new Client.Response(
                    Message, `Couldn't convert your **Arguments** into an integer.`
                )
            }

            const Server = Arguments[0] ? Client.guilds.cache.get(Arguments[0]) : Message.guild

            if (!Server) {
                return new Client.Response(
                    Message, `Couldn't find a **Server** with the ID: **${Arguments[0]}**.`
                )
            }

            const Owner = await Server.fetchOwner()

            const VerificationLevels = {
                0: "None",
                1: "Low",
                2: "Medium",
                3: "High",
                4: "Highest",
            }

            const Emotes = {
                0: '50',
                1: '100',
                2: '150',
                3: '250'
            }

            Message.channel.send({
                embeds : [
                    new EmbedBuilder({
                        author : {
                            name : String(Message.member.displayName),
                            iconURL : Message.member.displayAvatarURL({
                                dynamic : true
                            })
                        },
                        title : `${Server.name}${Server.vanityURLCode ? ` (discord.gg/${Server.vanityURLCode})` : ''}`,
                        description : `Created: <t:${Math.floor(Server.createdTimestamp / 1000)}:f> (<t:${Math.floor(Server.createdTimestamp / 1000)}:R>)`,
                        fields : [
                            {
                                name : 'Information',
                                value : `Owner: **${Owner.user.tag}**\nLevel **${Server.premiumTier}**/**${Server.premiumSubscriptionCount}** boosts\nVerification: **${VerificationLevels[Server.verificationLevel]}**`,
                                inline : true
                        },
                            {
                                name : 'Artwork',
                                value : `Icon: ${Server.iconURL() !== null ? `[Click here](${Server.iconURL({ dynamic : true, size : 1024 })})` : '**N/A**'}\nBanner: ${Server.bannerURL() !== null ? `[Click here](${Server.bannerURL({ dynamic : true, size : 1024 })})` : '**N/A**'}\nSplash: ${Server.discoverySplashURL() !== null ? `[Click here](${Server.discoverySplashURL({ dynamic : true, size : 1024 })})` : '**N/A**'}`,
                                inline : true
                            },
                            {
                                name : 'Count',
                                value : `Roles: **${Server.roles.cache.size}**/250\nEmotes: **${Server.emojis.cache.size}**/${Emotes[Server.premiumTier]}\nBoosters: **${Server.members.cache.filter((m) => m.premiumSince !== null).size}**`,
                                inline : true
                            }
                        ],
                        footer : {
                            text : `Server ID: ${Server.id}`
                        },
                        thumbnail : {
                            url : Server.iconURL({
                                dynamic : true
                            })
                        }
                    }).setColor(Client.Color).setTimestamp()
                ]
            })
        } catch (Error) {
            return console.error(Error)
        }
    }
}