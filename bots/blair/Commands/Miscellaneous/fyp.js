const Command = require('../../Structures/Base/Command.js')
const { AttachmentBuilder } = require('discord.js')

const Phin = require('phin')

module.exports = class Fyp extends Command {
    constructor (Client) {
        super (Client, 'fyp', {

        })
    }

    async Invoke (Client, Message, Arguments) {
        Message.channel.sendTyping()

        try {
            const TikTok = await Phin({
                url : 'https://www.tikwm.com/api/feed/list',
                method : 'POST',
                parse : 'json',
                headers : {
                    'accept' : 'application/json, text/javascript, */*; q=0.01',
                    'content-type' : 'application/x-www-form-urlencoded; charset=UTF-8',
                    'sec-ch-ua' : '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
                },
                data : {
                    region : 'US',
                    count : 1,
                    cursor : 0,
                    web : 1,
                    hd : 1
                }
            })

            Message.reply({
                files : [
                    new AttachmentBuilder(
                        `https://www.tikwm.com${TikTok.body.data[0].play}`, { 
                            name : `blairForYou.mp4` 
                        }
                    )	
                ],
                allowedMentions : { 
                    repliedUser : false 
                }
            }).catch(() => {
                return // entity large
            })
        } catch (Error) {
            // Error

            console.error(Error)
        }
    }
}