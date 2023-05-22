
const{ MessageEmbed } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const db = require('quick.db')
module.exports = {
	name: 'eval',
	description: '',
	aliases:["pythonisass",],
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
          owner,
          "979978940707930143",
          "812126383077457921"
        ];
     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
   if (!authorized.includes(message.author.id)) return;

  


        const clean = text => {
            if (typeof (text) === "string")
                return text.replace(/`/g, "`" + String.fromCharCode(8203)).replace(/@/g, "@" + String.fromCharCode(8203));
            else
                return text;
        }
        try {
            const code = args.join(" ");

            let evaled = eval(code);

            if (typeof evaled !== "string")
                evaled = require("util").inspect(evaled);
            message.react(`<:down2:1010942456562462750> `)
            return message.reply(clean(evaled), { code: "xl" });
          
        } catch (err) {
            await message.reply(`\`ERROR\` \`\`\`xl\n${clean(err)}\n\`\`\``);
        }

	},
};