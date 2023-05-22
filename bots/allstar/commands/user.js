
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner,xmark,checked } = require("../config.json")
const db = require('quick.db')
const talkedRecently = new Set();
module.exports = {
	name: 'user',
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
  let pingemoji = `<:allstarconnection:996699189432025180>`

        if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {
              const authorized = [
            owner,
          "839221856976109608",
        ];
     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
     if (!authorized.includes(message.author.id)) return 
         if(!args[0] == 'unblacklist'){
                             let database = db.get(`blacklisted`)
                  if(database) {
                      let data = database.find(x => x.user ===  args[1])

                      if(!data) return message.react(`<:warn:1033072412188737638> `)
                    
                      let value = database.indexOf(data)
                      delete database[value]
                    
                      var filter = database.filter(x => {
                        return x != null && x != ''
                      })
                    
                    message.react('<:allstarcheckpng:1033072384258883624>')
                    
                  }
         }else if(args[0] == 'blacklist'){
                         let data = {
    user: args[1]
}
              db.push(`blacklisted`,data)
         }
      message.react(`<:allstarcheckpng:1033072384258883624> `)

        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};