const Command = require('../Command.js');
const Discord = require('discord.js')
const ReactionMenu = require('../ReactionMenu.js');
const moment = require('moment');

module.exports = class BoostersCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'boosters',
            aliases: ['boosts', 'boostercount'],
            usage: 'boosters',
            type: client.types.INFO,
            description: 'A list of current boosters',
            subcommands: ['boosters']
        });
    }
    async run(message) {
        const boosters = message.guild.members.cache.filter(m => m.premiumSince)
        let num = 1
        const list = boosters.map(x => `\`${num++}\` **${x.user.tag}** : ${moment(x.premiumSinceTimestamp).format('LLLL')}`)
        if (!list.length) return this.send_error(message, 1, `There are **no boosters** for this server`)
        let tier
        if(message.guild.premiumTier.toString() === 'NONE') tier = 'No tier'
        if(message.guild.premiumTier.toString() === 'TIER_1') tier = 'Level **1**'
        if(message.guild.premiumTier.toString() === 'TIER_2') tier = 'Level **2**'
        if(message.guild.premiumTier.toString() === 'TIER_3') tier = 'Level **3** (vanity)'
        const embed = new Discord.MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({
                dynamic: true
            }))
            .setTitle(`Boosters`)
            .setDescription(list.join('\n'))
            .setFooter(`There are ${list.length} current boosters - ${message.guild.premiumSubscriptionCount} boosts`)
            .setColor(this.hex)
            .addField(`Premium Tier`, `${tier}`)
            .setTimestamp()
        if (list.length <= 10) {
            message.channel.send({ embeds: [embed] });
        } else {
            new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
    }
};