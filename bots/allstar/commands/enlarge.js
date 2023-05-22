
const{ MessageEmbed,Util,MessageActionRow,MessageButton } = require('discord.js');
const parse = require('../regex.js')
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'enlarge',
	description: 'enlarge mentioned emoji',
	aliases:['e'],
	usage: ' \```YAML\n\n enlarge {emoji} \``` ',
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
              const emoji = args[0];
        if (!args[0]) {
            const enlargeEmbed = new MessageEmbed()
               .setDescription(`${xmark} You must provide an emote to enlarge `)
            .setColor(error)
            if (!args[0]) return message.reply({embeds:[enlargeEmbed]})
        }
        let custom = Util.parseEmoji(emoji);
        const embed = new MessageEmbed()
        .setColor(color);

        if (custom.id) {
            embed.setImage(`https://cdn.discordapp.com/emojis/${custom.id}.${custom.animated ? "gif" : "png"}`);
            return message.channel.send({
              embeds:[embed],
             components:[
                new MessageActionRow()
        .addComponents(
         new MessageButton()
         .setLabel('Download')
         .setURL(`https://cdn.discordapp.com/emojis/${custom.id}.${custom.animated ? "gif" : "png"}`)
         .setStyle('LINK'),
        )
              ]
            });
        }
        else {
            let parsed = parse(emoji, { assetType: "png" });
            if (!parsed[0]) return message.reply({embeds:[new MessageEmbed().setDescription(`${xmark} You must provide a valid emote`).setColor(error)]})

            embed.setImage(parsed[0].url);
              const row = new MessageActionRow()
        .addComponents(
         new MessageButton()
         .setLabel('Invite Me!')
         .setURL(parsed[0].url)
         .setStyle('LINK'),
        )
            return message.channel.send({
              embeds:[embed],
              components:[
                new MessageActionRow()
        .addComponents(
         new MessageButton()
         .setLabel('Download')
         .setURL(parsed[0].url)
         .setStyle('LINK'),
        )
              ]
            });
        }

      
    
      
        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};