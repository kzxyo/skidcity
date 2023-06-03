const Subcommand = require('../../Subcommand.js');
const fetch = require('node-fetch')
const ReactionMenu = require('../../ReactionMenu.js');
const moment = require('moment');
const { MessageEmbed } = require('discord.js');
const Discord = require('discord.js');
const { stripIndent } = require('common-tags');

module.exports = class Posts extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'instagram',
            name: 'stream',
            aliases: ['watch', 'start', 'add'],
            type: client.types.SEARCH,
            usage: 'instagram add [channel] [account]',
            userPermissions: ['MANAGE_GUILD'],
            description: 'IDKKK',
        });
    }
    async run(message, args) {
        
        if (!args.length) return this.help(message)
        if(this.db.get(`instagram_stream_${message.guild.id}`)) return this.send_error(message, 1, `You already have an ongoing stream. Please cancel it.`)
        const Insta = require('scraper-instagram');
        const InstaClient = new Insta();
        InstaClient.authBySessionId('5584450039%3Ar5kqVztO7tdFEd%3A23')
        const channel = this.functions.get_channel(message, args[0])
        const User = args[1]
        if (!User) return this.send_error(message, 1, `Provide a user`)
        const check = await InstaClient.getProfile(User)
        if(!check || check.private) return this.send_error(message, 1, `Cannot stream posts from **[${User}](${check.link})** due to their account privacy settings`)
        this.send_success(message, `Streaming posts from **${User}** to ${channel}`)
        this.db.set(`instagram_stream_${message.guild.id}`, {channel: channel.id, user: User})
        message.client.logger.info(`Subscribing to Instagram profile: ${User} in ${message.guild.name}`) 
        InstaClient.subscribeUserPosts(`${User}`, async (post, err) => {
            if (post) {
                post = await InstaClient.getPost(post.shortcode)
                if (post.contents.length && post.contents[0].type === 'photo') {
                    const embed = new MessageEmbed()
                        .setAuthor(`${post.author.name !== '' ? post.author.name : post.author.username}`, post.author.pic)
                        .setTitle(post.author.username + ` ${post.author.verified ? '<:verified:859242659339042836>' : ''}`)
                        .setFooter('Instagram', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/1024px-Instagram_icon.png')
                        .setURL(`https://instagram.com/p/${post.shortcode}`)
                        .setColor("f26b31")
                        .setDescription(stripIndent`${post.caption}`)
                        .setImage(post.contents[0].url)
                        .setTimestamp(new Date(post.timestamp * 1000))
                    channel.send({ embeds: [embed] })
                }
                else {
                    post = await InstaClient.getPost(post.shortcode)
                    const embed = new MessageEmbed()
                        .setAuthor(`${post.author.name !== '' ? post.author.name : post.author.username}`, post.author.pic)
                        .setTitle(post.author.username + ` ${post.author.verified ? '<:verified:859242659339042836>' : ''}`)
                        .setFooter('Instagram', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/1024px-Instagram_icon.png')
                        .setURL(`https://instagram.com/p/${post.shortcode}`)
                        .setColor("f26b31")
                        .setDescription(stripIndent`${post.caption}`)
                        .setTimestamp(new Date(post.timestamp * 1000))
                    channel.send({ embeds: [embed], files: [post.contents[0].url] })
                }
            } 
        }, {
            interval: 60,
            lastPostShortcode: 'slattnem',
            fullPosts: false,
        })
    }
}