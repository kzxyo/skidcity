const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

const Phin = require('phin')

module.exports = class TikTok extends Command {
    constructor (Client) {
        super (Client, 'tiktok', {
            Aliases : [ 'tt' ]

            // Add more info in a bit.
        })
    }

    async Invoke (Client, Message, Arguments) {
        if (!Arguments[0]) {
            return new Client.Help(
                Message, {
                    About : 'Get profile information for given TikTok username.',
                    Syntax : 'tiktok (Username)'
                }
            )
        }

        try {
            const TikTok = await Phin({
                url : 'https://www.tikwm.com/api/user/info',
                method : 'POST',
                parse : 'json',
                headers : {
                    'accept' : 'application/json, text/javascript, */*; q=0.01',
                    'content-type' : 'application/x-www-form-urlencoded; charset=UTF-8',
                    'sec-ch-ua' : '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
                },
                data : {
                    unique_id : String(Arguments[0]).toLowerCase(),
                    count : 12,
                    cursor : 0,
                    web : 1,
                    hd : 1
                }
            })

            Message.channel.send({
                embeds : [
                    new EmbedBuilder({
                        author : {
                            name : String(Message.member.displayName),
                            iconURL : Message.member.displayAvatarURL({
                                dynamic : true
                            })
                        },
                        title : `${TikTok.body.data.user.uniqueId !== TikTok.body.data.user.nickname ? `${TikTok.body.data.user.nickname} (@${TikTok.body.data.user.uniqueId})` : TikTok.body.data.user.uniqueId} ${TikTok.body.data.user.privateAccount ? ':lock:' : TikTok.body.data.user.verified ? ':ballot_box_with_check:' : ''}`,
                        url : `https://tiktok.com/@${TikTok.body.data.user.uniqueId}`,
                        description : String(TikTok.body.data.user.signature),
                        fields : [
                            {
                                name : 'Following',
                                value : String(parseInt(TikTok.body.data.stats.followingCount).toLocaleString()),
                                inline : true
                            },
                            {
                                name : 'Followers',
                                value : String(parseInt(TikTok.body.data.stats.followerCount).toLocaleString()),
                                inline : true
                            },
                            {
                                name : 'Likes',
                                value : String(parseInt(TikTok.body.data.stats.heartCount).toLocaleString()),
                                inline : true
                            }
                        ],
                        thumbnail : {
                            url : TikTok.body.data.user.avatarLarger
                        }
                    }).setColor('#c6bfc6')
                ]
            })
        } catch (Error) {
            // Error Function (Database)
            console.log(Error)
        }
    }
}