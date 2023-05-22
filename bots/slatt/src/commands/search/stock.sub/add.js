const Subcommand = require('../../Subcommand.js');
const fetch = require('node-fetch')
const ReactionMenu = require('../../ReactionMenu.js');
const moment = require('moment');
const { MessageEmbed } = require('discord.js');
const Discord = require('discord.js')

module.exports = class Posts extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'stock',
            name: 'add',
            aliases: ['watch', 'start'],
            type: client.types.SEARCH,
            usage: 'stock add [channel] tick1, tick2, tick3',
            userPermissions: ['MANAGE_GUILD'],
            description: 'Sgkfjmdkgmfkdfm',
        });
    }
    async run(message, args) {
        return
        if (!args.length) return this.help(message)
        const channel = this.functions.get_channel(message, args[0])
        const tickers = args.slice(1).join(' ').split(', ')
        const StockSocket = require("stocksocket");
        StockSocket.addTickers(tickers, stockPriceChanged);
        message.client.logger.info(`Opened stocksocket connection with Yahoo`)
        this.send_success(message, `Opened stream for **${tickers.join(', ')}** to ${channel}`)
        this.db.set(`stocks_${message.guild.id}`, {channel: channel.id, stocks: tickers})
        function stockPriceChanged(data) {
            const embed = new MessageEmbed()
            .setDescription(`**${data.id}** ($${Math.round(data.price)}) Change %: ${data.changePercent}`)
            .setColor('BLUE')
            channel.send({embeds: [embed]})
        }
    }
}