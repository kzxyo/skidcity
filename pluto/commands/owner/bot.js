const Discord = require('discord.js');

module.exports = {
config: {
		name: "setavatarbot",
		aliases: ["setbotpfp"]
},
		run: async (client, message, args) => {
	 let avatarurl = args.join(" ");
				const developers = ['1137846765576540171']

				if(!developers.includes(message.author.id)) { 
						message.reply('> no adrian perms lol')
						return
				}

				if(developers.includes(message.author.id)) {    client.user.setAvatar(`${avatarurl}`)
	 if (!avatarurl) return message.channel.send(`provide a image url`)
        const embed = new MessageEmbed()
  
                .setColor("#27272F")
                .setTitle(`New Avatar Set`)
                .setImage(`${avatar.url}`)

      const embed2 = new MessageEmbed()
  
      .setDescription(`<:approve:1215258414008242247> ${message.author}: Successfully set ${client.user.username}'s avatar to this`)
      .setImage(`${avatar.url}`)
	  .setImage(avatarurl)
	  .setColor(`#a3eb7b`)
  
      return message.channel.send({ embeds: [embed2] })
				
			};
	}
}
