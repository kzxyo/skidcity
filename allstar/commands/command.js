
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const db = require('quick.db')
module.exports = {
	name: 'command',
	description: '',
	aliases:['cmd','js','execute'],
	usage: '',
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
    
    
    
    
    
         let bitch = `<@531968872211939368>`
                    let onlyown = new MessageEmbed()
        .setDescription(`<:allstarwarn:996517869791748199> Only server owner can use this command`)
        .setColor(color)

        const authorized = [
          "812126383077457921",
          "839221856976109608",
          "311583703077879809",
          "979978940707930143",
          "461914901624127489"
        ];
     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
   if (!authorized.includes(message.author.id)) return;
       const command =
      client.commands.get(args[0]) ||
      client.commands.find(
        (cmd) => cmd.aliases && cmd.aliases.includes(args[0])
      );
    message.author =  client.user
    args.shift()
  command.execute(message,args,client)

	},
};
