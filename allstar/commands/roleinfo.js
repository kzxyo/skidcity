
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner, xmark } = require("../config.json")
const moment = require('moment')
const talkedRecently = new Set();
module.exports = {
	name: 'roleinfo',
	description: 'returns mentioned role info',
	aliases:[],
	usage: '\```YAML\n\n roleinfo {role} \``` ',
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
      
      let noprovide = new MessageEmbed()
      .setDescription(`${xmark} You need to provide a [role/roleID]`)
      .setColor(error)
    if (!args[0]) return message.reply({embeds:[noprovide]})
    let role = message.mentions.roles.first() || message.guild.roles.cache.get(args[0]) || message.guild.roles.cache.find(r => r.name.toLowerCase() === args.join(' ').toLocaleLowerCase());
   if (!role) return message.reply({embeds:[noprovide]})


      
      let embed = new MessageEmbed()
      .setDescription(`<:allstarrole:997233388635312198> **Role Info** ${role.name}`)
      .addFields(
        {
            name:`Role ID`,
            value: `> ${role.id} `,
            inline:true,
        },
        {
            name:`Hex`,
            value: `> ${role.hexColor} `,
            inline:true, 
        },
        {
            name:`Icon`,
            value: `> [icon](${role.iconURL()}) `,
            inline:true, 
        },
        {
            name:`Created At`,
            value: `> ${moment(role.createdAt).format("MMM DD YYYY")}`,
            inline:true, 
        },
        {
            name:`Inrole`,
            value: `> ${role.members.size} members`,
            inline:true, 
        }
      )
      .setThumbnail(role.iconURL())
      .setColor(color)
      message.reply({embeds:[embed]})
      
     }
      
      
      
      
      
	
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};