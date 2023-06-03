
const{ MessageEmbed, Permissions  } = require('discord.js');
const db = require('quick.db')
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'antibot',
	description: 'kicks every bot added in the server',
	aliases:[],
	usage: ' \```antibot [on/off]\``` ',
  category: "security",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
        let emoji = `<:887705796476018688:989122635705233418> `;
            if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {

    let checkenable = new MessageEmbed()
    .setDescription(`<:allstarenabled:996521189986021386> Anti Bot Is Enabled `)
    .setThumbnail(`https://cdn.discordapp.com/attachments/991601306747813978/996704762110148688/IconServerSecurity_1.gif`)
    .setColor(color)
    let checkdisabled = new MessageEmbed()
    .setDescription(`<:allstardisabled:996521221749481516>  Anti Bot Is Disabled `)
    .setThumbnail(`https://cdn.discordapp.com/attachments/991601306747813978/996704762110148688/IconServerSecurity_1.gif`)
    .setColor(color)
            let onlyown = new MessageEmbed()
        .setDescription(`${xmark} Only server owner can use this command`)
        .setColor(error)

        const authorized = [
            message.guild.ownerId,
            owner
        ];
     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
   if (!authorized.includes(message.author.id)) return message.reply({embeds:[onlyown]}).catch(() => {/*Ignore error*/})

     let aenabled = new MessageEmbed().setDescription(`${checked} Anti Bot is now enabled`).setColor(color) 
               let missperms = new MessageEmbed()
        .setDescription(`${xmark}  You're missing \`MANAGE_GUILD\``)
        .setColor(error)
               
        let nukeable = new MessageEmbed()
        .setDescription(`${checked} Anti Bot enabled`)
        .setColor(color)
 if (args[0] == 'on') {
if (!authorized.includes(message.author.id)) return message.reply({embeds:[onlyown]});
      if (await db.has(`anti-bot_${message.guild.id}`) === false) {

        await db.set(`anti-bot_${message.guild.id}`, true)
        message.reply({ embeds:[nukeable]}).catch(() => {/*Ignore error*/})

      } else return message.reply({ embeds:[aenabled]}).catch(() => {/*Ignore error*/})
    } else if (args[0] == 'off') {
         let disabled = new MessageEmbed()
         .setDescription(`${checked} Anti Bot is now disabled`)
         .setColor(color)
          let alreadydisabled = new MessageEmbed()
         .setDescription(`${xmark} Anti Bot is disabled`)
         .setColor(error)
      if (await db.has(`anti-bot_${message.guild.id}`) === true) {

        await db.delete(`anti-bot_${message.guild.id}`);
        message.reply({ embeds:[disabled]}).catch(() => {/*Ignore error*/})

      } else return message.reply({ embeds:[alreadydisabled]}).catch(() => {/*Ignore error*/})
    } if(!args[0]){
       let antibot = db.get(`anti-bot_${message.guild.id}`)
       if(antibot !== true) {return message.reply({embeds:[checkdisabled]}).catch(() => {/*Ignore error*/}) } 
      else if(antibot === true) {return message.reply({embeds:[checkenable]}).catch(() => {/*Ignore error*/}) }
      
    }else if(args[0] == 'info'){
            let embed11 = new MessageEmbed()
        .setDescription(`\<:allstarbots:996652601170993202> Anti Bot \n <:allstar:1001031487103193108> antibot [on/off] info :\`kicks every new bot if it's enabled \``)
 
        .setColor(color)
        message.reply({embeds:[embed11]}).catch(() => {/*Ignore error*/})
      
    }
	}

            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};