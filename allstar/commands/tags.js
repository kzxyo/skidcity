
const{ MessageEmbed,MessageButton, MessageActionRow } = require('discord.js');
const db = require('quick.db')
const { default_prefix ,color,error,owner,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'tags',
	description: '\```YAML\n\n display available 0001 tags \```',
	aliases:[],
	usage: '\``` tags\```',
    category: 'utility',
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
    //  if(message.guild.id !== '1031650118375571537') return
      if(!message.member.premiumSinceTimestamp) { 
                const authorized = [
          owner
        ];
   if (!authorized.includes(message.author.id)) return message.reply({embeds:[new MessageEmbed().setDescription(`${xmark} This is a booster only command!`).setColor(error)]})
      
      }
      
            
      const data = db.get(`tags`) || 'no availabe tags'
        if(data === null) return message.reply({embeds:[{description:`No available tags `,color:error}]})
    let i0 = 0;
      let i1 = 10;
      let page = 1;

      let description =
        `Available 0001 tags - ${data.length}\n\n` +
        data
          //.sort((a, b) => b.highest - a.highest)
          .reverse()
          .map(r => r)
          .map((r, i) => `\`${i + 1}\` - ${r.tag.tags} ${r.tag.time}`)
          .slice(0, 10)
          .join("\n");


               const button1 = new MessageButton()
      .setCustomId('previousbtn')
      .setEmoji("<a:left:1033526539188449310>")
      .setStyle('PRIMARY');
            let invite2 = new MessageButton()
         .setLabel('Invite')
         .setURL("https://discord.com/api/oauth2/authorize?client_id=938863295543251024&permissions=8&scope=bot%20applications.commands")
         .setStyle('LINK')
      const button2 = new MessageButton()
      .setCustomId('nextbtn')
      .setEmoji("<:right:1033526800401317928> ")
      .setStyle('PRIMARY');
       const button3 = new MessageButton()
      .setCustomId('fastp')
      .setEmoji("<:DW_X_Mark:1032345318127304806> ")
      .setStyle('DANGER');



    let buttonList = [
      button1,
      button3,
      button2,
  ]
    const row = new MessageActionRow().addComponents(buttonList);
        let embed = new MessageEmbed()

        .setColor(color)
       // .setThumbnail(message.guild.iconURL({dynamic:true,size:4096}))
        .setFooter({text:`Page - ${page}/${Math.ceil(data.length / 10)}`})
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
                  `Available 0001 tags - ${data.length}\n\n` +
                 data
                    //.sort((a, b) => b.highest - a.highest)
                     .reverse()
                    .map(r => r)
                       .map((r, i) => `\`${i + 1}\` - ${r.tag.tags} ${r.tag.time}`)
                    .slice(i0, i1)
                    .join("\n");
      
                embed
                  .setFooter(
                    `Page - ${page}/${Math.round(data.length / 10 + 1)}`
                  )
                  .setDescription(description)
              //   .setThumbnail(message.guild.iconURL({dynamic:true,size:4096}));
                  curPage.edit({ embeds: [embed] });
              break;
             case buttonList[1].customId:
              curPage.delete()
              break;
            case buttonList[2].customId:
              i0 = i0 + 10;
              i1 = i1 + 10;
              page = page + 1;
    
              if (i1 > message.guild.roles.size + 10) {
                return;
              }
              if (!i0 || !i1) {
                return;
              }
    
              description =
                `Available 0001 tags - ${data.length}\n\n` +
                data
                 // .sort((a, b) => b.highest - a.highest)
                  .reverse()
                  .map(r => r)
                  .map((r, i) => `\`${i + 1}\` - ${r.tag.tags} ${r.tag.time}`)
                  .slice(i0, i1)
                  .join("\n");
    
              embed
              //  .setThumbnail(message.guild.iconURL({dynamic:true,size:4096}))
                .setFooter(
                  {text:`Page - ${page}/${Math.round(data.length / 10 + 1)}`}
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
         
      
      
        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};