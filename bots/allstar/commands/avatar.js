
const{ MessageEmbed,MessageButton,MessageActionRow } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'avatar',
	description: 'returns mentioned user profile picture',
	aliases: ["av",'pfp'],
	usage: ' \```YAML\n\n avatar {heist#0001} \``` ',
  category: "utility",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async (message, args, client) => {
        
            if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {

  
        
        

      let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ')) || client.users.cache.find(r => r.tag === args.join(' ')) || client.users.cache.get(args[0]) || message.member

  
try {
         const row = new MessageActionRow()
        .addComponents(
         new MessageButton()
         .setLabel('webp')
          .setEmoji("<:MessageLink:1010885859735785553>")
         .setURL(`${mentionedMember.displayAvatarURL({format: "webp", dynamic: true, size: 4096})}`)
         .setStyle('LINK'),
        )
        .addComponents(
         new MessageButton()
         .setLabel('jpg')
          .setEmoji("<:MessageLink:1010885859735785553>")
           .setURL(`${mentionedMember.displayAvatarURL({format: "jpg", dynamic: true, size: 4096})}`)
         .setStyle('LINK'),
        )
        .addComponents(
         new MessageButton()
         .setLabel('png')
          .setEmoji("<:MessageLink:1010885859735785553>")
          .setURL(`${mentionedMember.displayAvatarURL({format: "png", dynamic: true, size: 4096})}`)
           .setStyle('LINK'),
          )
         
          let embed = new MessageEmbed()
          .setImage((mentionedMember.displayAvatarURL({ format: "png", dynamic: true, size: 4096 })))
          .setFooter({ text: `${mentionedMember.user.tag}`})
          .setColor(color)
          await message.reply({embeds:[embed] , components: [row]}).catch(() => {/*Ignore error*/})
        }catch{
        
            const row = new MessageActionRow()
      .addComponents(
       new MessageButton()
       .setLabel('webp')
        .setEmoji("<:MessageLink:1010885859735785553>")
       .setURL(`${message.author.displayAvatarURL({format: "webp", dynamic: true, size: 4096})}`)
       .setStyle('LINK'),
      )
      .addComponents(
       new MessageButton()
       .setLabel('jpg')
        .setEmoji("<:MessageLink:1010885859735785553>")
         .setURL(`${message.author.displayAvatarURL({format: "jpg", dynamic: true, size: 4096})}`)
       .setStyle('LINK'),
      )
      .addComponents(
       new MessageButton()
       .setLabel('png')
        .setEmoji("<:MessageLink:1010885859735785553>")
        .setURL(`${message.author.displayAvatarURL({format: "png", dynamic: true, size: 4096})}`)
       .setStyle('LINK'),
      )
        let embed = new MessageEmbed()
        .setImage((message.author.displayAvatarURL({ format: "png", dynamic: true, size: 4096 })))
        .setFooter({ text: `${message.author.tag}`})
        .setColor(color)
        await message.reply({embeds : [embed] , components: [row]}).catch(() => {/*Ignore error*/})

      
        }
	}
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};