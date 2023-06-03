
const{ MessageEmbed,MessageButton,MessageActionRow } = require('discord.js');
const axios = require('axios')
const ms = require('moment')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'serverinfo',
	description: 'returns servers info ',
	aliases:["sinfo"],
	usage: '\```YAML\n\n serverinfo \``` ',
  category: "information",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
         let emoji = `<:allstar:1001031487103193108> `;
    //let levelemoji = `<:allstarboostlvl0:997557652525699213> `;
            if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {
       
        if (message.guild.premiumTier.includes('1')) {
          let levelemoji = `<:allstarboostlvl1:997557493360234596> `;
        }
      else if (message.guild.premiumTier.includes('2')) {
        let levelemoji = `<:allstarboostlvl2:997557538151211078> `;
      } else if (message.guild.premiumTier.includes('3')) {
        let levelemoji = `<:allstarboostlvl2:997557580836638830> `;
      } let levelemoji = `<:887705796476018688:989122635705233418>`
         let x = message.guild.vanityURLCode 
         let vanity =  'discord.gg/' + message.guild.vanityURLCode 
         if(x === null) vanity = `No vanity`
         
    const verificationLevels = {
      NONE: 'None',
      LOW: 'Low',
      MEDIUM: 'Medium',
      HIGH: 'High',
      VERY_HIGH: 'Highest'
    };  
          
                let embed = new MessageEmbed()
        .setAuthor({name:`${message.guild.name} `})
        .setThumbnail(message.guild.iconURL({dynamic:true}))
        .setColor(color)
        .setFooter({text:`${message.guild.id}`,iconURL:`https://media.discordapp.net/attachments/1006892159477219428/1016697567465197568/IconCopyID.png`})
        .addFields({
            name:`Owner`,
            value:`${emoji} ${client.users.cache.get(message.guild.ownerId).tag} \n **ID** (\`${message.guild.ownerId}\`) `,
            inline:true
        },
        {
          name:`Server Created`,
          value:`${emoji} ${ms(message.guild.createdAt).fromNow()} `,
          inline: true,
         },
      {
        name:`Roles`,
        value: `${emoji} ${message.guild.roles.cache.size}  `,
        inline:true,
    },

        {
            name:`Members`,
            value: `${emoji} **Total ${message.guild.memberCount}** \n${emoji} Users ${message.guild.memberCount -  message.guild.members.cache.filter(member => member.user.bot).size} \n${emoji} Bots ${message.guild.members.cache.filter(member => member.user.bot).size} `,
            inline: true,
        },
        {
            name:`Boost`,
            value: `${emoji} Level ${message.guild.premiumTier.replace('TIER_', '' && 'NONE','0')} \n${emoji} Boosts ${message.guild.premiumSubscriptionCount} `,
            inline: true,
        },

        {
          name:`Channels`,
          value: `${emoji} Text ${message.guild.channels.cache.filter(channel => channel.type == 'GUILD_TEXT').size} \n${emoji} Voice ${message.guild.channels.cache.filter(channel => channel.type == 'GUILD_VOICE').size}\n${emoji} Categories ${message.guild.channels.cache.filter(channel => channel.type == 'GUILD_CATEGORY').size}`,
          inline: true,
      },
        
        {
          name:`Emotes`,
          value: `${emoji} Emojis ${message.guild.emojis.cache.size} \n${emoji} Stickers ${message.guild.stickers.cache.size} `,
          inline:true,
      },
                  
        )
                
        const row = new MessageActionRow()
        .addComponents(
          new MessageButton()
          .setLabel('icon')
          .setEmoji("<:MessageLink:1010885859735785553>")
          .setURL(`${message.guild.iconURL({dynamic:true,size:4096})}`)
          .setStyle('LINK'),
         )
                const data = await axios.get(`https://discord.com/api/guilds/${message.guild.id}`, {
            headers:{
              Authorization:`Bot ${client.token}`
            }
          }).then(d => d.data);
          if(data.banner){
            let url = data.banner.startsWith("a_")?".gif?size=4096":".png?size=4096";
            url = `https://cdn.discordapp.com/banners/${message.guild.id}/${data.banner}${url}`
      

          


       if(url) row.addComponents(
         new MessageButton()
         .setLabel('banner')
         .setEmoji("<:MessageLink:1010885859735785553>")
         .setURL(`${url}`)
         .setStyle('LINK'),
        )
          
         if(message.guild.splashURL()) row.addComponents(
         new MessageButton()
         .setLabel('splash')
         .setEmoji("<:MessageLink:1010885859735785553>")
         .setURL(`${message.guild.splashURL({format:"png",dynamic:false,size:4096})}`)
         .setStyle('LINK'),
        ) 

      



      /*
        let embed = new MessageEmbed()
        .setDescription(`${message.guild.name} \n <:allstar:1001031487103193108> ${message.guild.description}`)
        .setThumbnail(message.guild.iconURL({dynamic:true}))
        .setColor(color)
        .setFooter({text:`${message.guild.id}`,iconURL:`https://media.discordapp.net/attachments/1006892159477219428/1016697567465197568/IconCopyID.png`})
        .addFields({
            name:`Vanity`,
            value: `<:allstarinfo:997234551568994324> ${vanity}`,
            inline: true,
          
        },
        {
            name:`Members`,
            value: `<:allstarhumans:996652234261659718> ${message.guild.memberCount}`,
            inline: true,
        },{
            name:`Roles`,
            value:`<:allstarrole:997233388635312198>  ${message.guild.roles.cache.size}`,
            inline: true,
        },
        {
            name:`Channels`,
            value: `<:allstarchannell:996785609777614918> ${message.guild.channels.cache.size}`,
            inline: true,
        },
                {
            name:`Security`,
            value: `<:allstarsecurity:996512639666618518>  ${verificationLevels[message.guild.verificationLevel]}`,
            inline:true,
        },
        {
            name:`Server Owner`,
            value: `<:allstarowner:997232293355716688>  <@${message.guild.ownerId}>`,
            inline:true,
        },
        {
            name:`Server Created At`,
            value:`<:allstartime:997233251695480873>  ${message.guild.createdAt.toDateString()}`,
            inline: true,
        },
        {
            name:`Booster Count`,
            value: ` ${emoji} <:allstarboostlvl2:997557580836638830> Level ${message.guild.premiumTier.replace('TIER_', '' && 'NONE','0')} \n ${emoji} <:allstarboost:997232872509427833>  Boosts ${message.guild.premiumSubscriptionCount}`,
            inline: true,
        },

        {
            name:`Emojis`,
            value: `<:983302634171686922:1002539401177477120>  ${message.guild.emojis.cache.size} `,
            inline:true,
        },
                  
        ) */

        message.reply({embeds:[embed],components:[row]});

      
          
	}else return message.reply({embeds:[embed]})
          
  //  } else return  message.reply({embeds:[embed],components:[row]})
          

    } 
                                                
                                                
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};