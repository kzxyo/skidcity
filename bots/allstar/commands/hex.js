
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner,xmark } = require("../config.json")
const request = require('axios');
const talkedRecently = new Set();
module.exports = {
	name: 'hex',
	description: 'search a hex color',
	aliases:["color"],
	usage: ' \```YAML\n\n hex #000000 \```',
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
      let hexx = args[0].replace(`#`,``)

      request.get(`https://api.alexflipnote.dev/colour/${hexx}`)
      .then(data => {


        let shades = [data.data.shade[0], data.data.shade[1],data.data.shade[2],data.data.shade[3] ]
      let embed = new MessageEmbed()
      .setAuthor({name:`${data.data.name}`,iconURL:`${data.data.images.square}`})
      .addFields(
      {
        name:`RGB`,
        value:`${data.data.safe_text_colour.rgb.r},${data.data.safe_text_colour.rgb.g},${data.data.safe_text_colour.rgb.b}`,
        inline:true, 
      },
      {
        name:`HEX`,
        value:`${data.data.hex.clean}`,
        inline:true
      },
      {
        name:`Brightness`,
        value:`${data.data.brightness}`,
        inline:true
      }
      )

      .addField(`Shades`,'\```yaml\n\n' + shades + '\```')
      .setImage(data.data.images.gradient)
      .setThumbnail(data.data.images.square)
      .setColor(args[0])
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