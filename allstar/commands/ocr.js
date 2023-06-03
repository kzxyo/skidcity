
const{ MessageEmbed } = require('discord.js');
const axios = require('axios')
const { default_prefix ,color,error,owner ,xmark} = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'ocr',
	description: '',
	aliases:[],
	usage: '',
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
        if(message.attachments.first()){

        
        axios.get(`https://api.ocr.space/parse/imageurl?apikey=K86339484888957&url=${message.attachments.first().url}`)
        .then(response => {
             if(!response.data.ParsedResults.ParsedText && response.data.ParsedResults.ParsedText === null) return message.reply({embeds:[{description:`${xmark} Image doesn't contain text`,color:error}]})
            message.reply({embeds:[
                {
                    description:`${response.data.ParsedResults.ParsedText}`,
                    color:color
                }
            ]})
        })
    }else {
        axios.get(`https://api.ocr.space/parse/imageurl?apikey=K86339484888957&url=${args.join(" ")}`)
        .then(response => {
             if(!response.data.ParsedResults.ParsedText && response.data.ParsedResults.ParsedText === null) return message.reply({embeds:[{description:`${xmark} Image doesn't contain text`,color:error}]})
            message.reply({embeds:[
                {
                    description:`${response.data.ParsedResults.ParsedText}`,
                    color:color
                }
            ]})
        })
    }




          let embeds = new MessageEmbed()
        .setDescription(`> ${pingemoji} : ${Math.round(client.ws.ping)}ms.`)
        .setColor(color)
        message.reply({embeds:[embeds]})



        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};
