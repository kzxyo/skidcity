const Subcommand = require('../../Subcommand.js');
const { MessageEmbed } = require('discord.js')
const moment = require('moment')
const permissions = require('../../../utils/json/permissions.json');

module.exports = class Soundcloud extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'role',
            name: 'info',
            type: client.types.MOD,
            usage: 'role info [role]',
            description: 'View information on a specific role',
        });
    }
    async run(message, args) {
        if(!args.length) return this.help(message)
        let roleinfo = this.functions.get_role(message, args.join(' '))
        const finalPermissions = []
        const rolePermissions = roleinfo.permissions.toArray()
        for (const permission in permissions) {
            if (rolePermissions.includes(permission)) finalPermissions.push(`${permissions[permission]}`);
        }
        let perms
        if (finalPermissions.length < 10 || finalPermissions.length === 10) perms = finalPermissions.map(x => `${x}`).join(', ')
        if (finalPermissions.length > 10) perms = finalPermissions.slice(0, 10).map(x => `${x}`).join(', ') + ` and **${finalPermissions.length}** more`
        const embed = new MessageEmbed()
            .setAuthor(message.author.tag, message.author.avatarURL({
                dynamic: true
            }))
            .setTitle(`${roleinfo.name}`)
            .setDescription(`id: **${roleinfo.id}**\nmembers: **${roleinfo.members.size}**`)
            .addField(`Color`, `${roleinfo.hexColor || 'Unkown'}`, true)
            .addField(`Created`, `${moment(roleinfo.createdTimstamp).format('MMM DD YYYY')}`, true)
            .addField(`Position`, `${roleinfo.position || 'Unkown'}`, true)
            .addField('Permissions', `${perms || 'Unkown'}`)
            .setColor(this.hex);
        return message.channel.send({ embeds: [embed] })
    }
}