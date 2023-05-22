
const{ MessageEmbed } = require('discord.js');
const axios = require('axios')
const { default_prefix ,color,error,owner,checked } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'base64',
	description: 'encode a message with base64',
	aliases:[],
	usage: '\```base64 hello \```',
  category: "utility",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
    console.log("PING" + message.author.username)
        if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {

        axios.get(`https://some-random-api.ml/base64?encode=${args.join(' ')}`)
        .then(response => {
            message.reply({
                embeds:[
                    {

                        color:color,
                        fields: [
                          {
                            name: `${checked} Encoded ${args.join(' ')} `,
                            value: '\```' + `${response.data.base64}` + '\```'
                          }
                        ]
                      }
                ]
            })
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
