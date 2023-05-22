
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const moment = require("moment");
require("moment-duration-format");
const talkedRecently = new Set();
module.exports = {
	name: 'uptime',
	description: 'shows bots uptime ',
	aliases:[],
	usage: '\```uptime \```',
  category: "information",
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
        const style = 'R'
        const starttime = `<t:${Math.floor(client.readyAt / 1000)}` + (style ? `:${style}` : '') + '>'
        const duration = moment.duration(client.uptime).format(" D [days], H [hrs], m [mins], s [secs]");
        let onlyown = new MessageEmbed()
        .setDescription(`Only server owner can use this command`)
        .setColor(color)

        const authorized = [
            "839221856976109608"
           
        ];
     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
   //  if (!authorized.includes(authorized)) return;
        let embed = new MessageEmbed()
        .setDescription(` **Uptime** \n> • Mem Usage  :: ${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2)} MB \n> • Uptime     :: ${duration}`)
        .setTimestamp()
        .setColor(color)
        message.reply({embeds:[embed]});
	}
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};