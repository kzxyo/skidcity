const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const API = require('node-twitch').default, TwitchClient = new API({ client_id : process.env.TWITCH_CLIENT_ID, client_secret : process.env.TWITCH_CLIENT_SECRET })

const { fetch } = require('undici')

module.exports = class Twitch extends Command {
    constructor (bot) {
        super (bot, 'twitch', {
            description : 'Get information on a Twitch streamer',
            parameters : [ 'username' ],
            syntax : '(username)',
            example : 'siterip',
            module : 'Miscellaneous'
        })
    }

    async execute (bot, message, args) {
        try {
            const username = String(args[0]).toLowerCase()

            if (!args[0]) {
                return bot.help(
                    message, this
                )
            }

            message.channel.sendTyping()

            const [ AccessToken, user ] = await Promise.all(
                [
                    fetch(`https://id.twitch.tv/oauth2/token?client_id=${process.env.TWITCH_CLIENT_ID}&client_secret=${process.env.TWITCH_CLIENT_SECRET}&grant_type=client_credentials`, {
                        method : 'POST'
                    }).then((response) => response.json()),
                    TwitchClient.getUsers(username)
                ]
            )

            if (user.data.length === 0) {
                return bot.warn(
                    message, `Streamer [**${username}**](https://twitch.tv/${username}) doesn't exist`
                )
            } 

            const [ followers, stream ] = await Promise.all(
                [
                    fetch(`https://api.twitch.tv/helix/users/follows?to_id=${user.data[0].id}`, {
                        method : 'GET',
                        headers : {
                            Authorization : `Bearer ${AccessToken.access_token}`,
                            'Client-Id' : process.env.TWITCH_CLIENT_ID
                        }
                    }).then((response) => response.json()),
                    fetch(`https://api.twitch.tv/helix/streams?user_id=${user.data[0].id}`, {
                        method : 'GET',
                        headers : {
                            Authorization : `Bearer ${AccessToken.access_token}`,
                            'Client-Id' : process.env.TWITCH_CLIENT_ID
                        }
                    }).then((response) => response.json())
                ]
            )

            const { display_name, login, broadcaster_type, description, view_count, profile_image_url } = user.data[0]

            message.channel.send({
                embeds : [
                    new Discord.EmbedBuilder({
                        author : {
                            name : message.member.displayName,
                            iconURL : message.member.displayAvatarURL({
                                dynamic : true
                            })
                        },
                        title : `${display_name}${display_name !== login ? ` (@${login})` : ''}${broadcaster_type === 'partner' ? ' ☑️' : ''}`,
                        url : `https://www.twitch.tv/${login}`,
                        description : description || '',
                        fields : [
                            {
                                name : 'Followers',
                                value : followers.total.toLocaleString(),
                                inline : true
                            },
                            {
                                name : 'Total Views',
                                value : view_count.toLocaleString(),
                                inline : true
                            },
                            {
                                name : 'Status',
                                value : stream.data[0]?.type ? 'Live' : 'Offline',
                                inline : true
                            }
                        ],
                        thumbnail : {
                            url : profile_image_url
                        }
                    }).setColor(bot.colors.neutral)
                ]
            })
        } catch (error) {
            return bot.error(
                message, 'twitch', error
            )
        }
    }
}