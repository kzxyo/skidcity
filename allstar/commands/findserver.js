
const{ MessageEmbed } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'server',
	description: 'get info about a server from vanity ',
	aliases:[],
	usage: ' \```YAML\n\n server discord.gg/heist \``` ',
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
          let emoji = `<:887705796476018688:989122635705233418> `;
      client.fetchInvite(args[0]).then((invite) => {

        let xx = new MessageEmbed()
      .setDescription(`${xmark} Couldn't fetch that server `)
      .setColor(error)
        if(!invite) return message.reply({embeds:[xx]})
        if(!invite.guild) return message.reply({embeds:[xx]})
                         let x = invite.guild.vanityURLCode 
         let vanity = `discord.gg/` + invite.guild.vanityURLCode 
         if(x === null) vanity = `No vanity`
         
        
        
            const verificationLevels = {
      NONE: 'None',
      LOW: 'Low',
      MEDIUM: 'Medium',
      HIGH: 'High',
      VERY_HIGH: 'Highest'
    };
        let owner = invite.guild.ownerId 
        if(!owner) {
           owner = `couldn't cache `
        }
        else owner = `<@${invite.guild.ownerId}>`
              let embed = new MessageEmbed()
      .setColor(color)
              .setThumbnail(invite.guild.iconURL({dynamic:true , size:4096}))
              .addFields({
            name:`Vanity`,
            value: `<:allstarinfo:997234551568994324> ${vanity}`,
            inline: true,
          
        },
        {
            name:`Members`,
            value: `<:allstarhumans:996652234261659718> ${invite.guild.memberCount ||invite.memberCount || `couldn't cache`}`,
            inline: true,
        },
        {
            name:`Security`,
            value: `<:allstarsecurity:996512639666618518>  ${verificationLevels[invite.guild.verificationLevel]}`,
            inline:true,
        },
        {
            name:`Server Owner`,
            value: `<:allstarowner:997232293355716688>  ${owner  || `couldn't cache`}`,
            inline:true,
        },
        {
            name:`Server Created At`,
            value:`<:allstartime:997233251695480873>  ${invite.guild.createdAt.toDateString()}`,
            inline: true,
        },
        {
            name:`Booster Count`,
            value: ` <:allstarboost:997232872509427833>  ${invite.guild.premiumSubscriptionCount}`,
            inline: true,
        },

           )
        //.setFooter({text: message.author.tag ,iconURL: client.user.displayAvatarURL()})
         message.reply({embeds:[embed]});
      
  
    }).catch((err) => {
        console.log(err)
                let xx = new MessageEmbed()
      .setDescription(`${xmark} Couldn't fetch that server `)
      .setColor(error)
                message.reply({embeds:[xx]})
      })

      

      
      
      
        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 4700);
    }

	},
};