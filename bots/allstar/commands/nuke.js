
const{ MessageEmbed,Permissions,MessageActionRow,MessageButton } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'nuke',
	description: 'deletes current channel and clones it',
	aliases:["clone"],
	usage: ' \```YAML\n\n nuke [#channel] \```',
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
        .setDescription(`${xmark} You're missing \`MANAGE_CHANNELS\` permission`)
         .setColor(color)
               let imissperms = new MessageEmbed()
        .setDescription(`<:allstarwarn:996517869791748199>  i don't have perms`)
        .setColor(error)
        if (!message.guild.me.permissions.has([ Permissions.FLAGS.MANAGE_CHANNELS])) return message.reply({ embeds:[imissperms]});
        if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_CHANNELS]))  return message.channel.send({ embeds:[missperms]});
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
            new MessageEmbed().setDescription(`Are you sure you want to nuke this channel?.`).setColor(color)
          ],
                         components:[row]
                        }).then(m => {
            if(!m) return;
            setTimeout(() => { m.delete().catch(()=> {})},3500)
          }).catch(() => { /* */})
         // const filter = (i) => {
        //    if(i.author.id === message.author.id) return true
        //  }
          
          const collector = message.channel.createMessageComponentCollector({
            filter: i => i.user.id === message.author.id,
            max:1
          })
          
          collector.on("end", (ButtonInteraction) => {
           
            const id = ButtonInteraction.first().customId;
            if(id === 'yes') {
             let embed = new MessageEmbed()
          .setDescription(`${checked} Channel Nuked by ${message.author.tag}`)
          .setColor(color)
          message.channel.clone().then(channel => {
              //channel.setPosition(message.channel.position)
              channel.send({embeds:[embed]})
          })
          message.channel.delete().catch(() => {/*Ignore error*/})
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
          
          
          
          /*
          let embed = new MessageEmbed()
          .setTitle(`${checked} Channel Nuked by ${message.author.tag}`)
          .setColor(color)
          message.channel.clone().then(channel => {
              //channel.setPosition(message.channel.position)
              channel.send({embeds:[embed]})
          })
         // message.channel.delete().catch(() => {/*Ignore error*/ //}) 
          // */
	}
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};