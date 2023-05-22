const{ MessageEmbed,MessageActionRow,MessageButton } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
const axios = require('axios')
module.exports = {
	name: 'banner',
	description: 'returns mentioned user banner',
	aliases: ["ub"],
	usage: ' \```YAML\n\n banner {user_mention} \```',
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
      try {

    let nobanner = new MessageEmbed()
          .setImage(`https://images-ext-1.discordapp.net/external/QnVBXMmbnt8ksbjQ1LEa7Pd3sd995EgaTr3J1p923JA/%3Fcolour%3D5263440%26w%3D1024%26h%3D205/https/image.sx4.dev/api/colour?width=922&height=184`)
          .setColor(color)
    
          //.setFooter({text: message.author.tag ,iconURL: client.user.displayAvatarURL()})

          let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || client.users.cache.get(args[0])
     
        if(!mentionedMember) {
          const data = await axios.get(`https://discord.com/api/users/${message.author.id}`, {
            headers:{
              Authorization:`Bot ${client.token}`
            }
          }).then(d => d.data);
          if(data.banner){
            let url = data.banner.startsWith("a_")?".gif?size=4096":".png?size=4096";
            url = `https://cdn.discordapp.com/banners/${message.author.id}/${data.banner}${url}`
                      let embed = new MessageEmbed()
          .setImage(url)
          .setColor(color)
          //.setFooter({text: message.author.tag ,iconURL: client.user.displayAvatarURL()})
                                    const row = new MessageActionRow()
        .addComponents(
         new MessageButton()
         .setLabel('webp')
         .setEmoji("<:MessageLink:1010885859735785553>")
         .setURL(url)
         .setStyle('LINK'),
        )
        .addComponents(
         new MessageButton()
         .setLabel('jpg')
         .setEmoji("<:MessageLink:1010885859735785553>")
           .setURL(url)
         .setStyle('LINK'),
        )
        .addComponents(
         new MessageButton()
         .setLabel('png')
         .setEmoji("<:MessageLink:1010885859735785553>")
          .setURL(url)
         .setStyle('LINK'),
        )
          await message.reply({embeds:[embed],components:[row]}).catch(() => {/*Ignore error*/})
          } else {
            message.reply({embeds:[nobanner]})
          }
   } else {
               const data = await axios.get(`https://discord.com/api/users/${mentionedMember.id}`, {
            headers:{
              Authorization:`Bot ${client.token}`
            }
          }).then(d => d.data);
          if(data.banner){
            let url = data.banner.startsWith("a_")?".gif?size=4096":".png?size=4096";
            url = `https://cdn.discordapp.com/banners/${mentionedMember.id}/${data.banner}${url}`
                      let embed = new MessageEmbed()
          .setImage(url)
          .setColor(color)
                                                          const row = new MessageActionRow()
        .addComponents(
         new MessageButton()
         .setLabel('webp')
         .setEmoji("<:MessageLink:1010885859735785553>")
         .setURL(url)
         .setStyle('LINK'),
        )
        .addComponents(
         new MessageButton()
         .setLabel('jpg')
         .setEmoji("<:MessageLink:1010885859735785553>")
           .setURL(url)
         .setStyle('LINK'),
        )
        .addComponents(
         new MessageButton()
         .setLabel('png')
         .setEmoji("<:MessageLink:1010885859735785553>")
          .setURL(url)
         .setStyle('LINK'),
        )
          //.setFooter({text: mentionedMember.tag ,iconURL: client.user.displayAvatarURL()})
          await message.reply({embeds:[embed],components:[row]}).catch(() => {/*Ignore error*/})
          } else {

          message.reply({embeds:[nobanner]})
           
            
          }
     
   }
      
    } catch {}
 //
	}
          talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};