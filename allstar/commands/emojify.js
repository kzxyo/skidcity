
const{ MessageEmbed } = require('discord.js');
const axios = require('axios')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'emojify',
	description: 'emojify an argument',
	aliases:[],
	usage: '\```emojify lucky \```',
  category: "utility",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
  let pingemoji = `<:allstarconnection:996699189432025180>`

        if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {
        axios.get(`https://luminabot.xyz/api/text/emojify?text=${args.join(" ")}`)
              .then(response => {
            let embed = new MessageEmbed()
            .setDescription(`${response.data.emojifyed}`)
            .setColor(color)
            message.reply({embeds:[embed]})
        })


        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};