
const{MessageEmbed, MessageActionRow ,MessageButton} = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const db = require('quick.db')
const os = require("os");
const moment = require("moment");
require("moment-duration-format");
const talkedRecently = new Set();
module.exports = {
	name: 'info',
	description: '\u200B',
	aliases:['botinfo'],
	usage: '\``` botinfo \```',
  category: "information",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client,files) => {
                if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {
      

    
      let memoryUsage = `${Math.round(process.memoryUsage().heapUsed / 1024 / 1024 * 100) / 100}MB`;
      const duration = moment.duration(client.uptime).format(" D [days], H [hrs], m [mins], s [secs]");
    const row = new MessageActionRow()
        .addComponents(
         new MessageButton()
         .setLabel('Invite Me!')
          .setEmoji("<:MessageLink:1010885859735785553>")
         .setURL("https://discord.com/api/oauth2/authorize?client_id=938863295543251024&permissions=8&scope=bot%20applications.commands")
         .setStyle('LINK'),
        )
        .addComponents(
         new MessageButton()
         .setLabel('Support Server!')
          .setEmoji("<:MessageLink:1010885859735785553>")
         .setURL("https://discord.gg/heist")
         .setStyle('LINK'),
        )
         .addComponents(
         new MessageButton()
         .setLabel('Privacy Policy!')
          .setEmoji("<:MessageLink:1010885859735785553>")
         .setURL("https://nek0.gitbook.io/allstar/details/privacy-policy")
         .setStyle('LINK'),
        )
 
        let embed = new MessageEmbed()
        .setAuthor({name:`Allstar Info`,iconURL:`${client.user.displayAvatarURL()}`})
        .setDescription('\```' + `Developed and maintained by ${client.users.cache.get('839221856976109608').tag}` + '\```')
        .addFields(
        {
          name:`Client`,
          value:`<:allstar:1001031487103193108> Users ${client.guilds.cache.reduce((a, g) => a + g.memberCount, 0)} \n <:allstar:1001031487103193108> Servers ${client.guilds.cache.size} \n <:allstar:1001031487103193108> Commands ${client.commands.size} \n <:allstar:1001031487103193108> Shard ${message.guild.shardId} \n <:allstar:1001031487103193108> Ping ${client.ws.ping} \n <:allstar:1001031487103193108> Commands Used ${db.get('commandsused')} `,
          inline:true
        },
        {
          name:`Stats`,
          value:`<:allstar:1001031487103193108> Memory Usage (${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2)}/${(require('os').totalmem() / 1024 / 1024).toFixed(2)}) \n <:allstar:1001031487103193108> CPU Cores ${require('os').cpus().length} \n <:allstar:1001031487103193108> Uptime ${duration}`,
          inline:true
        },

        )
        .setThumbnail(client.user.displayAvatarURL())
        .setTimestamp()
        .setColor(color)
        message.reply({ embeds: [embed], components: [row]});
      
	}
          talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};