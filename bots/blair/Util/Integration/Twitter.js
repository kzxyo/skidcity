const Twit = require('twit')

const { EmbedBuilder, AttachmentBuilder } = require('discord.js')

module.exports = class Twitter {
    constructor (Client) {
        this.Client = Client

        this.Twitter = new Twit({
            consumer_key : process.env.TwitterApiKey,
            consumer_secret : process.env.TwitterApiSecret,
            access_token : process.env.TwitterAccessToken,
            access_token_secret : process.env.TwitterAccessTokenSecret,
            timeout_ms : 60 * 1000
        })
    }

    async Start () {
        this.Client.Database.query('SELECT * FROM twitters').then(async ([Results]) => {
            this.Stream(Results.map((Result) => Result.account_id))
        })
    }

    async Stream (Accounts) {
        console.log(Accounts)
        const StreamX = this.Twitter.stream('statuses/filter', { follow : Accounts })

        StreamX.on('tweet', async (Tweet) => {
            console.log(Tweet)
            this.Client.Database.query(`SELECT * FROM twitters WHERE account_handle = '${Tweet.user.screen_name}'`).then(async ([Results]) => {
                console.log(Results)
                for (const Result of Results) {
                    const Channel = this.Client.channels.cache.get(Result.channel_id)

                    if (Channel) {
                        Channel.send({
                            embeds : [
                                new EmbedBuilder({
                                    author : {
                                        name : Tweet.user.name,
                                        iconURL : Tweet.user.profile_image_url_https,
                                        url : `https://twitter.com/${Tweet.user.screen_name}`
                                    },
                                    description : Tweet.text,
                                    footer : {
                                        text : Tweet.source.split('>')[1].replace('</a', ''),
                                        iconURL : 'https://blair.win/assets/image/twitter.png'
                                    }
                                }).setTimestamp().setColor('#1DA1F2')
                            ]
                        })
                    }
                }
            })
        })

        this.Client.on('twitterStreamAdd', async () => {
            setTimeout(() => {
                StreamX.stop()
                this.Propagate()
            }, 5000)
        })
    }

    async Propagate () {
        this.Client.Database.query('SELECT * FROM twitters').then(async ([Results]) => {
            this.Stream(Results.map((Result) => Result.account_id))
        })
    }
}