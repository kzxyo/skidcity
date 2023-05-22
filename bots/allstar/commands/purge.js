
const{ MessageEmbed,Permissions } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'purge',
	description: 'clear uwanted messages',
	aliases:['clear','c'],
	usage: '\```YAML\n\n clear 100 \``` ',
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
        .setDescription(`${xmark} i don't have perms`)
        .setColor(error)
        let errorski = new MessageEmbed()
        .setDescription(`${xmark}  Make sure to put a number`)
        .setColor(error)
        let fraction = new MessageEmbed()
        .setDescription(`${xmark}  Make sure to put a fraction number `)
        .setColor(error)
        let limit = new MessageEmbed()
        .setDescription(`${xmark}  Max amount is 100 `)
        .setColor(error)
        let help = new MessageEmbed()
        .setDescription(`purge <<amount>> \n  example: purge 10 \n aliases : clear,c`)
        .setColor(color)
        if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {

        if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_MESSAGES]))  return message.reply({ embeds:[missperms]});
        if (!message.guild.me.permissions.has([ Permissions.FLAGS.MANAGE_MESSAGES])) return message.reply({ embeds:[imissperms]});
    

        if (!args[0]) return message.reply({embeds:[help]})
        const amountToDelete = Number(args[0], 10);
        if (isNaN(amountToDelete)) return message.reply({embeds:[errorski]})
        if (!Number.isInteger(amountToDelete)) return message.reply({embeds:[fraction]})
        if (!amountToDelete || amountToDelete < 2 || amountToDelete > 100) return message.reply({embeds:[limit]})
        const fetched = await message.channel.messages.fetch({
          limit: amountToDelete
        });
            let purged = new MessageEmbed()
            .setDescription(`${checked} Purged ${fetched.size} Messages`)
            .setColor(color)
 
            await message.channel.bulkDelete(fetched).catch(() => {})
            return message.channel.send({embeds:[purged]}).then(msg => {
              msg.delete({ timeout: 1000 })
            }).catch(() => { message.reply(`failed`)}),
            

        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id),
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }


	},
};
