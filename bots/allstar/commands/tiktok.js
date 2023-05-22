
const{ MessageEmbed,MessageAttachment,MessageActionRow,MessageButton } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const axios = require('axios')

const talkedRecently = new Set();
module.exports = {
	name: 'tiktok',
	description: '',
	aliases:["tt"],
	usage: '\```tiktok https://tiktok \```',
  category: "utility",
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

  
        

      
                  message.channel.sendTyping().catch(console.error)

              axios.get(`https://api.rival.rocks/tiktok?url=${args[0]}&api-key=0fe401ac-8ca9-4885-8973-7619eab605ad`)
                .then(async response => {
                        var link = `${response.data.items}`
                               const row = new MessageActionRow()

                              .addComponents(
                                  new MessageButton()
                                    .setLabel('Video Link')
                                    .setEmoji("<:tiktok:1038387756021334026> ")
                                    .setURL(`${args[0]}`)
                                    .setStyle('LINK'),
                                   )
                            message.delete()
                      await message.channel.send({files:[
                        {
                            attachment: link,
                            name: 'allstar.mp4'
                        }
                      ],embeds:[
                        new MessageEmbed()
                        .addField(`<:tiktok:1038387756021334026>   @${response.data.username}(${response.data.nickname})`,`> ${response.data.desc} \n> \`💬\` ${response.data.stats.comment_count_formatted} \`👍\` ${response.data.stats.digg_count_formatted} \`🔗\` ${response.data.stats.download_count_formatted}  (${response.data.stats.play_count_formatted} views)  \n> \`🎵\`  ${response.data.music.title}  ( ${response.data.music.author}) `)
                        .setFooter({text:`requested by : ${message.author.tag}`})
                        .setColor("#000000")
                      ],components:[row]})
                        message.channel.stopTyping()
                          .catch(err => { console.log(error)}); // if sending of the Discord message itself failed
                  })
                   
                    
                          .catch(err => { console.log(error)});  // if axios.get() failed
      
  



        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};