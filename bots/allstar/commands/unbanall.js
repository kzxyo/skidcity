
const{ MessageEmbed, Permissions,MessageActionRow,MessageButton  } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'unbanall',
	description: 'unban all banned users in the server',
	aliases:["massunban"],
	usage: ' \```YAML\n\n massunban \``` ',
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
        .setDescription(`${xmark}  i don't have perms`)
        .setColor(error)
            if (!message.member.permissions.has([ Permissions.FLAGS.BAN_MEMBERS]))  return message.reply({ embeds:[missperms]});
        if (!message.guild.me.permissions.has([ Permissions.FLAGS.BAN_MEMBERS])) return message.reply({ embeds:[imissperms]});

       

      
                const row = new MessageActionRow().addComponents(
             new MessageButton()
              .setCustomId('yes')
              .setEmoji("<:Blurple_check:1013176396861931630>")
              .setStyle('SECONDARY'),
            
            new MessageButton()
              .setCustomId('no')
              .setEmoji("<:DW_X_Mark:1013176426763145216>")
              .setStyle('SECONDARY')
          )
          let msg = message.reply({embeds:[
            new MessageEmbed().setDescription(`Are you sure you want to unban everyone ?.`).setColor(color)
          ],
                         components:[row]
                        }).then(m => {
            if(!m) return;
            setTimeout(() => { m.delete().catch(()=> {})},6500)
          }).catch(() => { /* */})
         // const filter = (i) => {
        //    if(i.author.id === message.author.id) return true
        //  }
          
          const collector = message.channel.createMessageComponentCollector({
            filter: i => i.user.id === message.author.id,
            max:1
          })
          
          collector.on("end",async (ButtonInteraction) => {
           
            const id = ButtonInteraction.first().customId;
            if(id === 'yes') {

        let nobannded = new MessageEmbed()
        .setTitle(`${xmark}  There are no banned users`)
        .setTimestamp()
        .setColor(error)
        let embed = new MessageEmbed()
        .setTitle(`${checked}  Unbanning everyone`)
        .setTimestamp()
        .setColor(color)

      await message.guild.bans.fetch().then(async (bans) => {
        if(bans.size == 0) return message.reply({embeds:[nobannded]})
          bans.forEach(async ban => {
          message.guild.members.unban(ban.user.id)
        })
        //message.reply({embeds:[embed]})
      }).then(async () => {     
         await message.reply({embeds:[embed]})
      })
            }
            if(id === 'no') {
                           let embed = new MessageEmbed()
          .setTitle(`Canceled`)
          .setColor(color)
            message.channel.send({embeds:[
              new MessageEmbed().setDescription(`${checked} Succesfully Canceled`).setColor(color)
            ]})
            }
          })
    
	}
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};
