const { MessageEmbed } = require("discord.js")
const moment = require('moment')
const db = require('quick.db')
module.exports = async (client, oldPresence, newPresence) => {
    let bl = [
        '816901373713973279'
    ]
    if(bl.some(x => x === newPresence.userId)) return
    if (!newPresence) return
    if (!oldPresence) return
    const new_status = newPresence.activities.filter(s => s.name === 'Custom Status')
    const old_status = oldPresence.activities.filter(s => s.name === 'Custom Status')
    const on = await client.db.vanity_status.findOne({ where: { guildID: newPresence.guild.id } })
    if (on) {
        const role_id = await client.db.vanity_role.findOne({ where: { guildID: newPresence.guild.id } })
        if (role_id !== null) {
            const channel_id = await client.db.vanity_channel.findOne({ where: { guildID: newPresence.guild.id } })
            const msg = await client.db.vanity_message.findOne({ where: { guildID: newPresence.guild.id } })
            const status_needed = on.status
            const status_check = Boolean(newPresence.clientStatus.web || newPresence.clientStatus.mobile || newPresence.clientStatus.desktop)
            const role = newPresence.guild.roles.cache.get(role_id !== null ? role_id.role : null)
            const channel = newPresence.guild.channels.cache.get(channel_id !== null ? channel_id.channel : null)
            if (1 === 1) {
                try {
                    if (!old_status.length
                        && new_status.length
                        && new_status[0].state.includes(status_needed) || old_status.length && !old_status[0].state.includes(status_needed)
                        && new_status.length && new_status[0].state.includes(status_needed)
                        && status_check === true) {
                        const member = newPresence.guild.members.cache.get(newPresence.userId)
                        await member.roles.add(role);
                        if (!member.roles.cache.has(role.id)) {
                            client.logger.info(`Status role added in ${newPresence.guild.name} - added ${role.name} to ${member.user.tag}`)
                            client.utils.send_log_message(newPresence, member, 'vanityrole', `${member.user.tag} added vanity to status\n> old status: **${old_status.length ? old_status[0].state : 'none'}**\n> new status: **${new_status.length ? new_status[0].state : 'none'}**`)
                            if (channel && msg !== null) channel.send(client.utils.replace_all_variables(msg.message, newPresence, member))
                        }
                    } else if (status_check === true
                        && old_status.length
                        && old_status[0].state.includes(status_needed)
                        && !new_status.length || new_status.length && old_status[0].state.includes(status_needed)
                        && !new_status[0].state.includes(status_needed) && status_check === true) {
                        const member = newPresence.guild.members.cache.get(newPresence.userId)
                        await member.roles.remove(role);
                        if (member.roles.cache.has(role.id)) {
                            client.logger.info(`Status role removed in ${newPresence.guild.name} - removed ${role.name} from ${member.user.tag}`)
                            client.utils.send_log_message(newPresence, member, 'vanityrole', `${member.user.tag} removed vanity from status\n> old status: **${old_status.length ? old_status[0].state : 'none'}**\n> new status: **${new_status.length ? new_status[0].state : 'none'}**`)
                        }
                    }
                } catch (error) {
                }
            }
        }
    }
}