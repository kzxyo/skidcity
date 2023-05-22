
const{ MessageEmbed,MessageActionRow,MessageButton,xmark  } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'bans',
	description: 'Just a test command',
	aliases:[],
	usage: '\```bans\```',
  category: "moderation",
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
      if(message.author.id !== '839221856976109608') return;
      
      message.guild.bans.fetch().then(async bans => {
        
      
      let i0 = 0;
      let i1 = 10;
      let page = 1;

      let description =
        `Total Bans - ${bans.size}\n\n` +
        bans
        .sort((a, b) => bans.size - bans.size)
        .map(r => r)
        .map(
        (r, i) => `**${i + 1}** - ${r.user.username} | ID - ${r.user.id}`)
          .slice(0, 10)
          .join("\n\n");


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
        .setFooter({text:`Page - ${page}/${Math.ceil(bans.size / 10)}`})
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
                  `Total Bans - ${bans.size}\n\n` +
                  bans
                    .map(r => r)
        .map(
        (r, i) => `**${i + 1}** - ${r.user.username} | ID - ${r.user.id}`)
                     .slice(0, 10)
                    .join("\n\n")
                    .slice(i0, i1)
                    .join("\n\n");
      
                embed
                  .setFooter(
                    `Page - ${page}/${Math.round(bans.size / 10 + 1)}`
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
    
              if (i1 > bans.size + 10) {
                return;
              }
              if (!i0 || !i1) {
                return;
              }
    
              description =
                `Total Bans - ${bans.size}\n\n` +
                 bans
                    .map(r => r)
                            .map(
        (r, i) => `**${i + 1}** - ${r.user.username} | ID - ${r.user.id}`)
                     .slice(0, 10)
                  .slice(i0, i1)
                  .join("\n\n");
    
              embed
                .setFooter(
                  {text:`Page - ${page}/${Math.round(bans.size / 10 + 1)}`}
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
        })
         

	}
    }
};