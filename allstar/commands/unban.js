
const{ MessageEmbed, Permissions  } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'unban',
	description: 'unban a banned user but why would you?',
	aliases:["removeban"],
	usage: '\```YAML\n\n unban {banneduser.id} \```',
  category: "moderation",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
                if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {
        let missperms = new MessageEmbed()
         .setDescription(`${xmark} You're missing \`BAN_MEMBERS\` permission`)
        .setColor(error)
       let imissperms = new MessageEmbed()
        .setDescription(`${xmark} i don't have perms`)
        .setColor(error)
       let provideid = new MessageEmbed()
       .setDescription(`${xmark}  Provide me an ID to unban`)
       .setColor(error)
       let notbanned = new MessageEmbed()
       .setDescription(`${xmark} That user is not banned`)
       .setColor(error)
       let failedunban = new MessageEmbed()
       .setDescription(`${xmark} failed to unban that user`)
       .setColor(error)
       let worked = new MessageEmbed()
       .setDescription(`${checked} Succesfully Unbanned`)
       .setColor(color)
  
        if (!message.member.permissions.has([ Permissions.FLAGS.BAN_MEMBERS]))  return message.reply({ embeds:[missperms]});
        if (!message.guild.me.permissions.has([ Permissions.FLAGS.BAN_MEMBERS])) return message.reply({ embeds:[imissperms]});
    
          const ID = args[0];
          const user = await message.guild.bans.fetch(ID).catch(() => {/* */})
          if (!ID) {
            message.reply({ embeds:[provideid]});
          } else        
          if (!user) {
            message.reply({ embeds:[notbanned]});
          } else {
            message.guild.members.unban(ID).catch(() => {
              message.reply({ embeds:[failedunban]})
            })
            message.reply({ embeds:[worked]});
          }
      }
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
    }
  