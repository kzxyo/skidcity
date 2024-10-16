const { Message } = require('discord.js')
const Discord = require('discord.js');

module.exports = {
	name: 'pic',

	/**
	 * @param {Message} message
	 */

	run: async (client, message, args) => {
		if (!message.member.hasPermission("MANAGE_ROLES")) return message.reply({ embed: { color: "#efa23a", description: `${warn} ${message.author} please make sure to have the correct permissions` } });
		if (!message.guild.me.hasPermission("MANAGE_ROLES")) return message.reply({ embed: { color: "#efa23a", description: `${warn} ${message.author} please make sure I have permissions` } });

        const picEmbed = new MessageEmbed()

        .setColor("#2f3136")
        .setTitle(`${guildprefix}pic`)
        .setDescription('give user pic perms')
        .addFields(
        { name: '**usage**', value: `${guildprefix}pic {user}`, inline: false },
        { name: '**aliases**', value: 'none', inline: false },
        )
  
        message.channel.send({ embeds: [picEmbed] })

		let user = message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.member;

		const Member = message.mentions.members.first() || message.guild.members.cache.get(args[0])
		if (Member.id == message.author.id) return message.reply({ embed: { color: "2f3136", description: `${warn} ${message.author}: You cannot pic perms **yourself**` } })
		if (!Member) return message.reply({ embed: { color: "#efa23a", description: `${warn} ${message.author}: I was unable to find a member with that name` } })
		const role = message.guild.roles.cache.find(role => role.name.toLowerCase() === 'pic')
		if (!role) {
			try {
				message.reply({ embed: { color: "#efa23a", description: `${warn} ${message.author}: There was no **pic** role found` } }).then(embedMessage => {
					embedMessage.edit({ embed: { color: "#efa23a", description: `${warn} ${message.author}: trying to create the **pic** role` } })
				});

				let jailrole = await message.guild.roles.create({
					data: {
						name: 'pic',
						permissions: []
					}
				});
				message.guild.channels.cache.filter(c => c.type === 'text').forEach(async (channel, id) => {
					await channel.createOverwrite(jailrole, {
						ATTACH_FILES: true,
						EMBED_LINKS: true
					})
				});
				message.guild.channels.cache.filter(c => c.type === 'voice').forEach(async (channel, id) => {
					await channel.createOverwrite(jailrole, {
						VIEW_CHANNEL: false,
						CONNECT: false
					})
				});
				message.reply({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: The **pic** role has been created` } })
			} catch (error) {
				console.log(error)
				message.channel.send(error)
			}
		};
		let role2 = message.guild.roles.cache.find(r => r.name.toLowerCase() === 'pic')
		if (Member.roles.cache.has(role2.id)) return message.reply({ embed: { color: "#efa23a", description: `${warn} ${message.author}: the user **${user.user.tag}** already has pic perms` } })
		await Member.roles.add(role2)
		message.reply({ embed: { color: "#a3eb7b", description: `${approve}: **${user.user.tag}** has been given pic perms` } })
	}
}