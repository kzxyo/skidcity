
const{ MessageEmbed, Permissions  } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'unlock',
	description: 'unlock a locked channel',
	aliases:['unlockdown'],
	usage: '\```YAML\n\n unlock #channel \n unlock \``` ',
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
       .setDescription(`<:allstarwarn:996517869791748199> You're missing \`MANAGE_GUILD\` permission`)
        .setColor(error)
  if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_GUILD])) return message.reply({ embeds:[missperms]});
    
    let channel = message.mentions.channels.first();
    if (channel) {
      let reason = args.join(' ').slice(22) || 'Not Specified';
    } else {
      channel = message.channel;
    }

    if (channel.permissionsFor(message.guild.id).has('SEND_MESSAGES') === true)  {
      const lockchannelError2 = new MessageEmbed()
        .setDescription(`<:IconWarningCircle:995777375130353755>  ${channel.name} isn't locked!`)
        .setColor(error);

      return message.channel.send(lockchannelError2);
    }

    channel.permissionOverwrites.edit(message.guild.id, { SEND_MESSAGES: true });

    const embeds = new MessageEmbed()
      .setDescription(` <:TextActiveThreads:1010885877666435172> ${channel.name} unlocked `)
      .setColor(color);

    message.reply({embeds:[embeds]})
  }
      
      
      
        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    

	},
};