
const{ MessageEmbed,Permissions } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'purgeuser',
	description: 'clear mentioned users message',
	aliases:['clearuser','cu'],
	usage: '\```YAML\n\n cu @heist#0001 50 \``` ',
  category: "moderation",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
        let missperms = new MessageEmbed()
       .setDescription(`${xmark} You're missing \`MANAGE_MESSAGES\` permission`)
        .setColor(error)
        let imissperms = new MessageEmbed()
        .setDescription(`${xmark}  i don't have perms`)
        .setColor(error)
        let errorski = new MessageEmbed()
        .setDescription(`${xmark}  Make sure to put a number`)
        .setColor(error)
        let fraction = new MessageEmbed()
        .setDescription(`${xmark} You need to mention a user to purge `)
        .setColor(error)
        let limit = new MessageEmbed()
        .setDescription(`${xmark}  Max amount is 100 `)
        .setColor(error)
        let help = new MessageEmbed()
        .setDescription(`purgeuser <<amount>> \n  example: purgeuser 10 \n aliases : clearuser,cu`)
        .setColor(color)
        let helpx = new MessageEmbed()
        .setDescription(`${checked} Succesfully deleted message for that user`)
        .setColor(color)
        if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {

        if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_MESSAGES]))  return message.reply({ embeds:[missperms]});
        if (!message.guild.me.permissions.has([ Permissions.FLAGS.MANAGE_MESSAGES])) return message.reply({ embeds:[imissperms]});
    

        if (!args[0]) return message.reply({embeds:[help]})

        let member = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || client.users.cache.get(args[0])
   
        const amount = Number(args[1], 10);
        if (!member) return message.reply({embeds:[fraction]})
        if (!amount) return message.reply({embeds:[errorski]})
        if (isNaN(amount)) return message.reply({embeds:[errorski]})
        if (amount > 100) return message.reply({embeds:[limit]})
       let AllMessages = await message.channel.messages.fetch()
       let FilteredMessages = await AllMessages.filter(x => x.author.id === member.id)
       let deletedMessages = 0

  
      await message.channel.bulkDelete(FilteredMessages).catch(() => {})
     //  await FilteredMessages.forEach(msg => {
    //   if (deletedMessages >= amount) return
    //  msg.delete()
    //  deletedMessages++
    //}) 
      await message.channel.send({embeds:[helpx]}).then(m => m.delete())

        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id),
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }


	},
};