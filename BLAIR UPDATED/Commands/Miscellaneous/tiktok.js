const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const { fetch } = require('undici')

const commands = [
    'download', 'dl', 'videos', 'vids'
]

module.exports = class TikTok extends Command {
    constructor (bot) {
        super (bot, 'tiktok', {
            description : 'Get information on a TikTok profile',
            parameters : [ 'username' ],
            syntax : '(username)',
            example : '@MrBeast',
            aliases : [ 'tt' ],
            commands : [
                {
                    name : 'tiktok download',
                    description : 'Download videos from a TikTok profile',
                    parameters : [ 'username' ],
                    syntax : '(username)',
                    example : '@MrBeast',
                    aliases : [ 'dl', 'videos', 'vids' ],
                    flags : [
                        {
                            name : 'count',
                            description : 'The amount of videos to download',
                            aliases : [ 'c', 'amount', 'a' ],
                            converter : Number,
                            maximum : 35,
                            minimum : 1
                        }
                    ]
                }
            ],
            module : 'Miscellaneous'
        })
    }

    async execute (bot, message, args) {
        let username = String(args[0]).toLowerCase()

        if (!args[0]) {
            return bot.help(
                message, this
            )
        }

        if (commands.includes(username)) {
            switch (true) {
                case (username === 'download' || username === 'dl' || username === 'videos' || username === 'vids') : {
                    try {
                        username = String(args[1]).toLowerCase()

                        if (!args[1]) {
                            return bot.help(
                                message, this.commands[0]
                            )
                        }

                        message.channel.sendTyping()

                        const results = await fetch(`https://www.tikwm.com/api/user/info?unique_id=${username}`, {
                            method : 'POST'
                        }).then((response) => response.json())

                        if (!results.data) {
                            return bot.warn(
                                message, `Profile [**${username}**](https://www.tiktok.com/@${username}) doesn't exist`
                            )
                        }

                        const { user, stats } = results.data

                        if (stats.videoCount === 0) {
                            return bot.warn(
                                message, `Profile [**${user.uniqueId}**](https://www.tiktok.com/@${user.uniqueId}) doesn't have any videos`
                            )
                        }

                        const count = message.parameters['count']

                        if (count?.success === false) {
                            return bot.warn(
                                message, count.message
                            )
                        } 

                        const count_value = count?.value ?? 5

                        const msg = await bot.neutral(
                            message, `Downloading **${count_value}** ${count_value === 1 ? 'video' : 'videos'} from [**${user.nickname}**](https://www.tiktok.com/@${user.uniqueId})`
                        )

                        const results2 = await fetch(`https://tikwm.com/api/user/posts?count=${count_value}&unique_id=${user.uniqueId}`, {
                            method : 'POST'
                        }).then((response) => response.json())

                        const { videos } = results2.data

                        await Promise.all(videos.map((video, index) => {
                            if (index > count_value - 1) return

                            const random = bot.util.random()

                            return message.channel.send({
                                files : [
                                    new Discord.AttachmentBuilder(
                                        video.play, {
                                            name : `blairTikTok${random}.mp4`
                                        }
                                    )
                                ],
                                embeds : [
                                    new Discord.EmbedBuilder({
                                        author : {
                                            name : video.author.nickname,
                                            iconURL : video.author.avatar,
                                            url : `https://www.tiktok.com/@${video.author.unique_id}`
                                        },
                                        title : video.title?.slice(0, 256) || '',
                                        url : `https://www.tiktok.com/@${video.author.unique_id}/video/${video.video_id}`,
                                        footer : {
                                            text : `❤️ ${parseInt(video.digg_count).toLocaleString()} 💬 ${parseInt(video.comment_count).toLocaleString()} 🎬 ${parseInt(video.play_count).toLocaleString()} - ${message.author.tag}`,
                                            iconURL : 'https://seeklogo.com/images/T/tiktok-icon-logo-1CB398A1BD-seeklogo.com.png'
                                        },
                                        timestamp : new Date(video.create_time * 1000)
                                    }).setColor(bot.colors.neutral)
                                ]
                            })
                        })).then(() => {
                            msg.delete()
                        })
                    } catch (error) {
                        return bot.error(
                            message, 'tiktok download', error
                        )
                    }
                }
            }
        } else {
            try {
                message.channel.sendTyping()
                
                const results = await fetch(`https://www.tikwm.com/api/user/info?unique_id=${username}`, {
                    method : 'POST'
                }).then((response) => response.json())
                
                if (!results.data) {
                    return bot.warn(
                        message, `Profile [**${username}**](https://www.tiktok.com/@${username}) doesn't exist`
                    )
                }
                
                const { user, stats } = results.data

                console.log(results.data)
                
                message.channel.send({
                    embeds : [
                        new Discord.EmbedBuilder({
                            author : {
                                name : message.member.displayName,
                                iconURL : message.member.displayAvatarURL({
                                    dynamic : true
                                })
                            },
                            title : `${user.uniqueId !== user.nickname ? `${user.nickname} (@${user.uniqueId})` : `${user.uniqueId}`} ${user.privateAccount ? ':lock:' : user.verified ? ':ballot_box_with_check:' : ''}`,
                            url : `https://www.tiktok.com/@${user.uniqueId}`,
                            description : user.signature,
                            fields : [
                                {
                                    
                                    name : 'Likes',
                                    value : stats.heartCount.toLocaleString(),
                                    inline : true
                                },
                                {
                                    name : 'Followers',
                                    value : stats.followerCount.toLocaleString(),
                                    inline : true
                                },
                                {
                                    name : 'Following',
                                    value : stats.followingCount.toLocaleString(),
                                    inline : true
                                }
                            ],
                            thumbnail : {
                                url : user.avatarLarger
                            }
                        }).setColor(bot.colors.neutral)
                    ]
                })
            } catch (error) {
                return bot.error(
                    message, 'tiktok', error
                )
            }
        }
    }
}