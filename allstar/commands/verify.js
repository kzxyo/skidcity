
const{ MessageEmbed,MessageActionRow,MessageButton,xmark  } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'verify',
	description: 'Just a test command',
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
     
        const authorized = [
          "812126383077457921",
          "839221856976109608",
          "979978940707930143"
        ];
     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
   if (!authorized.includes(message.author.id)) return;


      
      


       const button = new MessageButton()
      .setCustomId('previousbtnas')
      .setEmoji("<:dick:1031696971053944832>")
      .setStyle('SECONDARY');



    let buttonList = [
      button,
  ]
    const row = new MessageActionRow().addComponents(buttonList);
        let embed = new MessageEmbed()
        .setColor('#c495f0')
        .setDescription('<:04_Bblack:996539341096624168> click the button to verify \n\n inv [allstar](https://discord.com/oauth2/authorize?client_id=938863295543251024&permissions=8&scope=bot%20applications.commands) & [vile](https://discord.com/api/oauth2/authorize?client_id=991695573965099109&permissions=8&scope=bot%20applications.commands)')
        .setTitle('Welc 2 Heist')
        .setThumbnail('https://cdn.discordapp.com/attachments/1006892159477219428/1018227457561726997/cbe021ea5492cd53da0f9f8ee08acefb.jpg' )
        .setFooter('inv allstar & vile')
   

     const curPage = await message.channel.send({
       embeds:[JSON.parse(args.join(" "))
         ], components:[row]
                                     })
  const filter = (i) =>
    i.customId === buttonList[0].customId 


const collector = await curPage.createMessageComponentCollector({
  //filter,
  filter: i => i.user.id === message.author.id,

});
        collector.on("collect", async (i) => {
          if(i.customId === 'previousbtn') {
          let user = message.guild.members.cache.get(i.user.id)
          await user.roles.add(`1000729038387687474`)
          
       await i.deferUpdate();
          }
          
    
          


           collector.resetTimer();
        });
         

	}
    }
};
