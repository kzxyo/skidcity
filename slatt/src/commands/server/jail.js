const Discord = require("discord.js");
const Command = require('../Command.js');
const db = require("quick.db")

module.exports = class PurgeCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'jail',
            type: client.types.SERVER,
            usage: `jail [member] [reason]`,
            clientPermissions: ['MANAGE_MESSAGES'],
            userPermissions: ['MANAGE_MESSAGES'],
            description: `send people to jail`,
            subcommands: ['jail']
        });
    }

    async run(message, args) {
        let jailmsg = await message.client.db.jail_message.findOne({ where: { guildID: message.guild.id } })
        const prefix = await message.client.db.prefix.findOne({ where: { guildID: message.guild.id } })
        let dbjail = await message.client.db.jail_channel.findOne({ where: { guildID: message.guild.id } })
        let jail = message.guild.channels.cache.get(dbjail ? dbjail.channel : null) || message.guild.channels.cache.find(channel => channel.name === "jail")
        let dbjailrole = await message.client.db.jail_role.findOne({ where: { guildID: message.guild.id } })
        var jailrole = message.guild.roles.cache.get(dbjailrole ? dbjailrole.role : null) || await message.guild.roles.cache.find(r => r.name === "Jailed")
        if (!jail) {
            try {
                await message.guild.channels.create('jail').then(c => {
                    c.permissionOverwrites.create(message.guild.id, {
                        SEND_MESSAGES: false,
                        VIEW_CHANNEL: false
                    })
                    if (jailrole) c.permissionOverwrites.create(jailrole, {
                        SEND_MESSAGES: true,
                        VIEW_CHANNEL: true
                    })
                })
            } catch (e) {
                console.log(e.stack);
            }
        }
        if (!jailrole) {
            try {
                jailrole = await message.guild.roles.create({
                    name: "Jailed",
                    color: "#000001",
                    permissions: []
                })
                message.guild.channels.cache.forEach(async (channel, id) => {
                    await channel.permissionOverwrites.create(jailrole.id, {
                        SEND_MESSAGES: false,
                        VIEW_CHANNEL: false
                    });
                    if (channel.name === 'jail') {
                        channel.permissionOverwrites.create(jailrole.id, {
                            SEND_MESSAGES: true,
                            VIEW_CHANNEL: true
                        })
                    }
                })

            } catch (e) {
                console.log(e.stack);
            }
            return this.send_error(message, 0, `jail not found.. dont worry i set it up. try **re-jailing**`)
        }
        let jailed_channel = jail || 'None'
        if (!args.length) {
            const embed = new Discord.MessageEmbed()
                .setColor(this.hex)
                .setTitle(`Jail Setting`)
                .setDescription(`showing all jail settings. to jail a user, use \`${prefix.prefix}jail [user]\``)
                .addField(`jail channel:`, `${jailed_channel}`)
                .addField(`jail role:`, jailrole)
                .addField(`jail message:`, jailmsg || `**{jailed.mention}** was sent to jail`)
                .setFooter(`check ${prefix.prefix}variables for the jail message variables`)
            return message.channel.send({ embeds: [embed] })
        }
        if (!args.length) {
            return this.help(message)
        }
        const member = this.functions.get_member(message, args[0])
        if (!member) {
            return this.invalidUser(message)
        }
        if (member.permissions.has("MANAGE_MESSAGES")) {
            return this.send_error(message, 0, "You can't jail staff members.")
        }
        if (member.id === message.author.id) {
            return this.send_error(message, 0, "You can't jail yourself.")
        }

        if (member.roles.cache.has(jailrole)) {
            return this.send_error(message, 0, `provided user already jailed.`)
        }

        if (jailmsg === null) {
            jailmsg = `**${member.user.tag}** has been jailed.`
        } else {
            jailmsg = jailmsg.message
        }
        await member.roles.add(jailrole)
        await message.client.db.jailed.create({
            userID: member.id
        })
        let reason = args.slice(1).join(' ');
        if (!reason) reason = 'no reason provided';
        if (reason.length > 1024) reason = reason.slice(0, 1021) + '...';
        message.client.utils.send_punishment({
            message: message,
            action: 'jailed',
            reason: reason,
            member: member,
        })
        const amount = (await message.client.db.history.findAll({ where: { guildID: message.guild.id, userID: member.id } })).length + 1
        await message.client.db.history.create({
            guildID: message.guild.id,
            userID: member.id,
            action: 'jailed',
            reason: reason,
            author: message.author.id,
            date: `${Date.now()}`,
            num: amount,
        })
        message.client.utils.send_log_message(message, member, this.name, `**{user.tag}** Sent to jail`)
        this.send_success(message, `**${member.user.tag}** was sent to jail ${reason === 'no reason provided' ? '' : `for **${reason}**`}`)
        jail = message.guild.channels.cache.get(dbjail ? dbjail.channel : null) || message.guild.channels.cache.find(channel => channel.name === "jail")
        jail.send(message.client.utils.replace_all_variables(jailmsg, message, member)
            .replace(/`?\{jailer.mention}`?/g, message.member)
            .replace(/`?\{jailed.mention}`?/g, member)
            .replace(/`?\{jailer.username}`?/g, message.member.user.username)
            .replace(/`?\{jailed.username}`?/g, member.user.username)
            .replace(/`?\{jailer.tag}`?/g, message.member.user.tag)
            .replace(/`?\{jailed.tag}`?/g, member.user.tag)
            .replace(/`?\{guild.name}`?/g, message.guild.name))
    }
}