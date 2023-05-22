
const{ MessageEmbed,MessageActionRow,MessageButton,Permissions  } = require('discord.js');
const { default_prefix ,color,error,owner,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'emojis',
	description: 'returns a list of all emojis in the server',
	aliases:['emoji-list'],
	usage: '\```emojis \```',
  category: "information",
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
    .setDescription(`${xmark} You're missing \`MANAGE_ROLES\` permission`)
    .setColor(error)
   let imissperms = new MessageEmbed()
    .setDescription(`${xmark} i don't have perms`)
    .setColor(error)

     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});

   // if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_ROLES]))  return message.reply({ embeds:[missperms]});
      
      
      let i0 = 0;
      let i1 = 10;
      let page = 1;

      let description =
        `Total Emojis - ${message.guild.emojis.cache.size}\n\n` +
        message.guild.emojis.cache
          //.sort((a, b) => b.highest - a.highest)
          .map(r => r)
          .map((r, i) => `\`${i + 1}\` - ${r} | ID - \`${r.id}\``)
          .slice(0, 10)
          .join("\n");


               const button1 = new MessageButton()
      .setCustomId('previousbtn')
      .setEmoji("<:allstarleft:1009905064695042138>")
      .setStyle('SECONDARY');
            let invite2 = new MessageButton()
         .setLabel('Invite')
         .setURL("https://discord.com/api/oauth2/authorize?client_id=938863295543251024&permissions=8&scope=bot%20applications.commands")
         .setStyle('LINK')
      const button2 = new MessageButton()
      .setCustomId('nextbtn')
      .setEmoji("<:allstarright:1009905118336012398> ")
      .setStyle('SECONDARY');
       const button3 = new MessageButton()
      .setCustomId('fastp')
      .setEmoji("<:DW_X_Mark:1013176426763145216>")
      .setStyle('SECONDARY');



    let buttonList = [
      button1,
      button3,
      button2,
  ]
    const row = new MessageActionRow().addComponents(buttonList);
        let embed = new MessageEmbed()

        .setColor(color)
        .setFooter({text:`Page - ${page}/${Math.ceil(message.guild.emojis.cache.size / 10)}`})
        .setDescription(description);

     const curPage = await message.channel.send({
       embeds:[embed
         ], components:[row]
                                     })
  const filter = (i) =>
    i.customId === buttonList[0].customId ||
    i.customId === buttonList[1].customId || 
    i.customId === buttonList[2].customId;

const collector = await curPage.createMessageComponentCollector({
  //filter,
  filter: i => i.user.id === message.author.id,

});
        collector.on("collect", async (i) => {
          //console.log(i.user.id)
          if(i.user.id !== message.author.id) return;
          switch (i.customId) {
            case buttonList[0].customId:
                i0 = i0 - 10;
                i1 = i1 - 10;
                page = page - 1;
      
                if (i0 + 1 < 0) {
                  console.log(i0)
                  return;
                }
                if (!i0 || !i1) {
                  return 
                }
      
                description =
                  `Total Emojis - ${message.guild.emojis.cache.size}\n\n` +
                 message.guild.emojis.cache
                    //.sort((a, b) => b.highest - a.highest)
                    .map(r => r)
                    .map(
                      (r, i) => `\`${i + 1}\` - ${r} | ID - \`${r.id}\``)
                    .slice(i0, i1)
                    .join("\n");
      
                embed
                  .setFooter(
                    `Page - ${page}/${Math.round(message.guild.emojis.cache.size / 10 + 1)}`
                  )
                  .setDescription(description);
      
                  curPage.edit({ embeds: [embed] });
              break;
             case buttonList[1].customId:
              curPage.delete()
              break;
            case buttonList[2].customId:
              i0 = i0 + 10;
              i1 = i1 + 10;
              page = page + 1;
    
              if (i1 > message.guild.emojis.size + 10) {
                return;
              }
              if (!i0 || !i1) {
                return;
              }
    
              description =
                `Total Emojis - ${message.guild.emojis.cache.size}\n\n` +
                message.guild.emojis.cache
                 // .sort((a, b) => b.highest - a.highest)
                  .map(r => r)
                  .map(
                    (r, i) => `\`${i + 1}\` - ${r} | ID - \`${r.id}\``)
                  .slice(i0, i1)
                  .join("\n");
    
              embed
                .setFooter(
                  {text:`Page - ${page}/${Math.round(message.guild.emojis.cache.size / 10 + 1)}`}
                )
                .setDescription(description);
    
                curPage.edit({ embeds: [embed] });
              break;
            default:
              break;
          }
              await i.deferUpdate();

           collector.resetTimer();
        });
         

	}
    }
};