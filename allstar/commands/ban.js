
const{ MessageEmbed,MessageButton,MessageActionRow, Permissions } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const db = require('quick.db')
const talkedRecently = new Set();
module.exports = {
	name: 'ban',
	description: 'ban mentioned user from the server',
	aliases:[],
	usage: '\```YAML\n\n ban @heist#0001 spamming ``` ',
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
       let example = new MessageEmbed()
       .setDescription(`${xmark} you need to provide a [User/ID]`)
       .setColor(error)
       let banyou = new MessageEmbed()
       .setDescription(`${xmark} You can't ban yourself`)
       .setColor(error)
       let invaliduser = new MessageEmbed()
       .setDescription(`${xmark} Invalid user`)
       .setColor(error)
       let unbannable = new MessageEmbed()
       .setDescription(`${xmark} Can't ban that user`)
       .setColor(error)
       let higherrole = new MessageEmbed()
       .setDescription(`${xmark} Can't ban a user with higher role than yours`)
       .setColor(error)
    
    
              if (!message.member.permissions.has([ Permissions.FLAGS.BAN_MEMBERS]))  return message.reply({ embeds:[missperms]});
          if (!message.guild.me.permissions.has([ Permissions.FLAGS.BAN_MEMBERS])) return message.reply({ embeds:[imissperms]});
          

          let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || client.users.cache.get(args[0])
  

          let reason = args.slice(1).join(" ");
          if (!reason) reason = message.author.tag + ' : No Reason Provided';
            
          if (!args[0]) return message.reply({ embeds: [example]})
          if (!mentionedMember) return message.reply({ embeds:[invaliduser]})
          if (mentionedMember.id == message.author.id) return message.reply({ embeds:[banyou]})
          
          if (!mentionedMember.bannable) return message.reply({ embeds: [unbannable]})
          if (message.member.roles.highest.comparePositionTo(mentionedMember.roles.highest) <= 0) return message.reply({ embeds:[higherrole]})

          //mentionedMember.send(`You got banned by ${message.author} in ${message.guild.name}`)

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
          new MessageEmbed().setDescription(`Are you sure you want to ban this user.`).setColor(color)
        ],
                       components:[row]
                      })

                       

     const collector = await message.channel.createMessageComponentCollector({
           
          filter: (i) => i.user.id === message.author.id,
                 
        });
         
         collector.on("end", async (ButtonInteraction) => {
           console.log(ButtonInteraction)
           const id = ButtonInteraction.first().customId;
           if(id === 'yes') {
            let embed = new MessageEmbed()
         .setDescription(`${checked} Banned `)
         .setColor(color)
         await message.guild.members.ban(mentionedMember,{
          days: 7,
          reason: reason
        }).catch(err => console.log(err)).then((e) =>message.channel.send({ embeds:[banned]}))
        await message.channel.send({embeds:[embed]})
        // message.channel.delete().catch(() => {/*Ignore error*/})
           }
           if(id === 'no') {
                          let embed = new MessageEmbed()
         .setTitle(`Canceled`)
         .setColor(color)
         await message.channel.send({embeds:[
             new MessageEmbed().setDescription(`${checked} Canceled`).setColor(color)
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