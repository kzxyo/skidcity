const Event = require('../../Structures/Base/event.js'), Discord = require('discord.js')

const { fetch } = require('undici')

const regexes = {
    TikTok : /^(?:https?:\/\/)?(?:www\.)?(?:tiktok\.com\/@(?:\w+)|tiktok\.com\/t\/(?:\w+)|vm\.tiktok\.com\/(?:\w+)|vt\.tiktok\.com\/(?:\w+))/i,
    Twitter : /https:\/\/twitter\.com\/(\w+)\/status\/\d+/,
    YouTube : /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?(?:\S*?&)?v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
}

const unshorten = require('unshorten.it')

const { TwitterScraper } = require('@tcortega/twitter-scraper')

module.exports = class MessageCreate extends Event {
    constructor (bot) {
        super (bot, 'messageCreate')
    }

    async execute (bot, message) {
        try {
            if (!message.guild || message.author.bot) {
                return
            }

            if (!message.member) message.member = await message.guild.members.fetch(message)

            let prefix = bot.prefixes[message.guild.id]

            if (!prefix) {
                const data = await bot.db.query('SELECT * FROM prefixes WHERE guild_id = $1', {
                    bind : [
                        message.guild.id
                    ]
                }).then(([results]) => results)

                prefix = data.length ? data[0].prefix : bot.prefix, bot.prefixes[message.guild.id] = prefix
            }

            const command = await new bot.CommandHandler(
                message, {
                    prefix : prefix
                }
            ).construct()

            if (message.content.trim() === `<@!${bot.user.id}>` || message.content.trim() === `<@${bot.user.id}>`) {
                message.reply(`hi :3 (prefix is \`${prefix}\`)`)
            }

            if (message.content && message.content.toLowerCase().startsWith('blair')) {
                const arg = message.content.split(' ')[1]

                switch (true) {
                    case (regexes.TikTok.test(arg)) : {
                        message.channel.sendTyping()

                        const unshort = await unshorten(arg)

                        const TikTok = await bot.redis.getHash(`tiktok:${unshort.split('?')[0]}`)

                        const video = Object.keys(TikTok).length ? JSON.parse(TikTok['cache']) : await fetch(`https://www.tikwm.com/api/?url=${unshort}`, {
                            method : 'POST'
                        }).then((response) => response.json())

                        if (video.code === -1) {
                            return bot.warn(
                                message, `Invalid **TikTok URL**`
                            )
                        }

                        message.delete()

                        bot.redis.setHash(`tiktok:${unshort.split('?')[0]}`, 'cache', video, 86400)

                        const { id, title, play, play_count, digg_count, comment_count, create_time, author, images } = video.data

                        const embed = new Discord.EmbedBuilder({
                            author : {
                                name : author.nickname,
                                iconURL : author.avatar,
                                url : `https://www.tiktok.com/@${author.unique_id}`
                            },
                            title : title,
                            url : `https://www.tiktok.com/@${author.unique_id}/video/${id}`,
                            footer : {
                                text : `❤️ ${digg_count.toLocaleString()} 💬 ${comment_count.toLocaleString()} 🎬 ${play_count.toLocaleString()}${Object.keys(TikTok).length ? ' (cached)' : ''} - ${message.author.tag}`,
                                iconURL : 'https://seeklogo.com/images/T/tiktok-icon-logo-1CB398A1BD-seeklogo.com.png'
                            },
                            timestamp : new Date (create_time * 1000)
                        }).setColor(bot.colors.neutral)

                        if (images) {

                        } else {
                            const random = bot.util.random(null, 13)      
                            
                            message.channel.send({
                                files : [
                                    new Discord.AttachmentBuilder(
                                        play, {
                                            name : `blairTikTok${random}.mp4`
                                        }
                                    )
                                ],
                                embeds : [
                                    embed
                                ]
                            })
                        }

                        break
                    }

                    case (regexes.Twitter.test(arg)) : {
                        message.channel.sendTyping()

                        const Scraper = await TwitterScraper.create();

                        const meta = await Scraper.getTweetMeta(arg)

                        const { id, created_at, description, isMedia, isVideo, favorite_count, retweet_count, reply_count, media_url } = meta

                        if (!isMedia || !isVideo) {
                            return bot.warn(
                                message, `There is no **media** associated with the [Tweet](${arg})`
                            )
                        }

                        message.delete()

                        const video = media_url[0].url, random = bot.util.random(null, 13)

                        const match = arg.match(regexes.Twitter)
                        
                        const username = match[1]

                        const results = await fetch(`https://api.twitter.com/1.1/users/show.json?screen_name=${username}`, {
                            method : 'GET',
                            headers : {
                                Authorization : `Bearer ${process.env.TWITTER_BEARER_TOKEN}`
                            }
                        }).then((response) => response.json())

                        const { name, screen_name, profile_image_url_https } = results

                        message.channel.send({
                            files : [
                                new Discord.AttachmentBuilder(
                                    video, {
                                        name : `blairTwitter${random}.mp4`
                                    }
                                )
                            ],
                            embeds : [
                                new Discord.EmbedBuilder({
                                    author : {
                                        name : name || screen_name,
                                        iconURL : profile_image_url_https.replace('_normal', ''),
                                        url : `https://twitter.com/${screen_name}`
                                    },
                                    title : description?.split('https://t.co/')[0],
                                    url : `https://twitter.com/${screen_name}/status/${id}`,
                                    footer : {
                                        text : `❤️ ${favorite_count.toLocaleString()} 💬 ${reply_count.toLocaleString()} 🔁 ${retweet_count.toLocaleString()} - ${message.author.tag}`,
                                        iconURL : 'https://discord.com/assets/4662875160dc4c56954003ebda995414.png'
                                    },
                                    timestamp : new Date (created_at)
                                }).setColor(bot.colors.neutral)
                            ]
                        })

                        break
                    }

                    case (regexes.YouTube.test(arg)) : {
                        message.channel.sendTyping()

                        const ID = arg.match(regexes.YouTube)[1]

                        const ytdl = require('ytdl-core')

                        const meta = await ytdl.getInfo(ID)

                        const { videoDetails : { title, lengthSeconds, publishDate, author : { name, user_url, thumbnails }, video_url } } = meta

                        if (lengthSeconds > 500) {
                            return bot.warn(
                                message, `Video exceeds **5 minutes**`
                            )
                        }

                        message.delete()

                        const format = meta.formats.find((f) => f.qualityLabel && f.audioBitrate)
                        
                        const stream = await ytdl.downloadFromInfo(meta, { format })

                        const random = bot.util.random(null, 13)
 
                        const statistics = await fetch(`https://yt.lemnoslife.com/noKey/videos?part=statistics&id=${ID}`).then((response) => response.json())

                        const { viewCount, likeCount, commentCount } = statistics.items[0].statistics

                        message.channel.send({
                            files : [
                                new Discord.AttachmentBuilder(
                                    stream, {
                                        name : `blairYouTube${random}.mp4`
                                    }
                                )
                            ],
                            embeds : [
                                new Discord.EmbedBuilder({
                                    author : {
                                        name : name,
                                        iconURL : thumbnails[0].url,
                                        url : user_url
                                    },
                                    title : title,
                                    url : video_url,
                                    footer : {
                                        text : `❤️ ${parseInt(likeCount).toLocaleString()} 💬 ${parseInt(commentCount).toLocaleString()} 👁️ ${parseInt(viewCount).toLocaleString()} - ${message.author.tag}`,
                                        iconURL : 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/YouTube_social_red_circle_%282017%29.svg/2048px-YouTube_social_red_circle_%282017%29.svg.png'
                                    },
                                    timestamp : new Date (publishDate)
                                }).setColor(bot.colors.neutral)
                            ]
                        })
                    }
                }
            }
        } catch (error) {
            console.error('Message Create', error)
        }
    }
}