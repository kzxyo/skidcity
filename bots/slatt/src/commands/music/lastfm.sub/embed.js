const Subcommand = require('../../Subcommand.js');
const embedbuilder = require('godembed')
const { MessageEmbed, MessageFlags } = require('discord.js')
module.exports = class Embed extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'lastfm',
            name: 'embed',
            type: client.types.LASTFM,
            usage: 'lastfm embed [embed]/check/view/delete\nlastfm embed steal [member]',
            description: 'Set a custom embed to be displayed',
        });
    }
    async run(message, args) {
        const prefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
        if (args.length === 0) {
            return this.send_info(message, `Use \`${prefix.prefix}variables\` to view a full list of variables`)
        }   
        if (args[0].toLowerCase() == "delete") {
            let check = await message.client.db.embed.findOne({ where: { userID: message.author.id } })
            if (check === null) {
                return this.send_error(message, 1, `You cannot delete your embed if you dont have one set`)
            } else {
                await message.client.db.embed.destroy({ where: { userID: message.author.id } })
                return this.send_success(message, `Your custom embed was **deleted**`)
            }
        }
        if (args[0].toLowerCase() == "check" || args[0].toLowerCase() == "view") {
            const member = this.functions.get_member_or_self(message, args.slice(1).join(' '))
            if (!member) {
                return this.invalidUser(message)
            }
            let check = await message.client.db.embed.findOne({ where: { userID: member.id } })
            if (check) {
                const embed = new MessageEmbed()
                    .setColor(this.hex)
                    .setTitle(`${member.user.tag}`)
                    .setFooter(message.author.tag, message.author.avatarURL({
                        dynamic: true
                    }))
                    .setThumbnail(member.user.displayAvatarURL({
                        dynamic: true
                    }))
                    .setAuthor(member.user.tag, member.user.displayAvatarURL({
                        dynamic: true
                    }))
                    .setDescription(`\`\`\`js\n${check.code}\`\`\``)
                return message.channel.send({ embeds: [embed] })
            } else {
                return this.send_error(message, 1, `**${member.user.tag}** Doesnt have a nowplaying embed`)
            }
        } else if (args[0].toLowerCase() == "steal") {
            if (!args[1]) return this.provideUser(message)
            const member = this.functions.get_member(message, args.slice(1).join(' '))
            if (!member) {
                return this.invalidUser(message)
            }
            let check = await message.client.db.embed.findOne({ where: { userID: member.id } })
            if (check) {
                let check2 = await message.client.db.embed.findOne({ where: { userID: message.author.id } })
                if (check2 !== null) {
                    await message.client.db.embed.update({ code: check.code }, { where: { userID: message.author.id } })
                } else {
                    await message.client.db.embed.create({ userID: message.author.id, code: check.code })
                }
                const em = new MessageEmbed()
                    .setColor(this.hex)
                    .setAuthor(member.user.tag, member.user.displayAvatarURL({ dynamic: true }))
                    .setTitle(`${member.user.username}'s embed`)
                    .setThumbnail(message.author.avatarURL({
                        dynamic: true
                    }))
                    .setDescription(`\`\`\`js\n${check.code}\`\`\``)
                message.channel.send({embeds: [em]})
            } else {
                return this.send_error(message, 1, `**${member.user.tag}** Doesnt have a nowplaying embed`)
            }
        } else {
            let check = await message.client.db.embed.findOne({ where: { userID: message.author.id } })
            if (!args.join(' ').includes('$')) return this.send_error(message, 1, `You didnt seem to provide any **embed paramaters**`)
            const {
                embed,
                errors
            } = embedbuilder(args.join(' '))
            if (check) {
                await message.client.db.embed.update({ code: args.join(' ') }, { where: { userID: message.author.id } })
            } else {
                await message.client.db.embed.create({ userID: message.author.id, code: args.join(' ') })
            }
            const em = new MessageEmbed()
                .setColor(this.hex)
                .setTitle(`Last.fm embed updated`)
                .setAuthor(message.author.tag, message.author.avatarURL({
                    dynamic: true
                }))
                .setThumbnail(message.author.avatarURL({
                    dynamic: true
                }))
                .setDescription(`\`\`\`js\n${args.join(' ')}\`\`\``)
            message.channel.send({embeds: [em]})
            if (errors.length > 0) {
                return this.send_error(message, 1, `An error has occured, try using \`${prefix.prefix}help embed\``)
            }

        }
    }
}