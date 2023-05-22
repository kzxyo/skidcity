const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder } = require('discord.js')

const Cheerio = require('cheerio')
const Axios = require('axios')

module.exports = class WeHeartIt extends Command {
    constructor (Client) {
        super (Client, 'weheartit', {
            Aliases :  [ 'whi' ]
        })
    }

    async Invoke (Client, Message, Arguments) {
        const Username = String(Arguments[0]).toLowerCase()

        try {
            if (!Arguments[0]) {
                return new Client.Help(
                    Message, {
                        About : 'Check profile information for given WeHeartIt username.',
                        Syntax : 'weheartit (Username)'
                    }
                )
            }

            const Account = await Axios.get(`https://weheartit.com/${Username}`)

            const Scrape = Cheerio.load(Account.data)
            var Array, Avatar, DisplayName, Description

            Scrape('a.avatar-large').each((i, element) => { 
                const AvatarURL = Scrape(element).find('img.avatar').attr('src') 
                Avatar = String(AvatarURL).trim()
            })

            Scrape('h1.text-overflow').each((i, element) => {
                const Nickname = Scrape(element).find('a').text()

                DisplayName = String(Nickname).trim()
            })

            Scrape('p.text-big').each((i, element) => {
                const AboutMe = Scrape(element).text()

                Description = String(AboutMe).trim() 
            })

            Scrape('ul.bg-white').each((i, element) => {
                const Scraped = Scrape(element).text()

                Array = String(Scraped).trim().split(/\s+/g)
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
                        title : `${Username !== String(DisplayName).toLowerCase() ? `${DisplayName} (@${Username})` : `${Username}`}`,
                        url : `https://weheartit.com/${Username}`,
                        description : String(Description),
                        fields : [
                            {
                                name : 'Followers',
                                value : Array[8],
                                inline : true
                            },
                            {
                                name : 'Posts',
                                value : Array[4],
                                inline : true
                            },
                            {
                                name : 'Collections',
                                value : Array[2],
                                inline : true
                            }
                        ],
                        thumbnail : {
                            url : Avatar
                        }
                    }).setColor(Client.Color)
                ]
            })
        } catch (Error) {
            if (Error.message === 'Request failed with status code 404') {
                return new Client.Response(
                    Message, `Couldn't find a **WeHeartIt** account with that username.`
                )
            }
            
            return new Client.Error(
                Message, 'weheartit', Error
            )
        }
    }
}