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
            name: 'stop',
            aliases: ['cancel', 'clear', 'end'],
            type: client.types.SEARCH,
            usage: 'instagram stop',
            userPermissions: ['MANAGE_GUILD'],
            description: 'IDKKK 2',
        });
    }
    async run(message, args) {
        return
        if (!this.db.get(`instagram_stream_${message.guild.id}`)) return this.send_error(message, 1, `You dont have an ongoing stream.`)
        const Insta = require('scraper-instagram');
        const InstaClient = new Insta();
        InstaClient.authBySessionId('5584450039%3Ar5kqVztO7tdFEd%3A23')
        const ig = this.db.get(`instagram_stream_${message.guild.id}`)
        this.send_success(message, `Ended instagram stream.`)
        message.client.logger.info(`Unsubscribing from Instagram profile: ${ig.user} in ${message.guild.name}`)
        InstaClient.subscribeUserPosts(`${ig.user}`, async (post, err) => {
        }).unsubscribe()
        this.db.delete(`instagram_stream_${message.guild.id}`)
    }
}