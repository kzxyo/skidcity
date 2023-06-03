const { MessageEmbed,Permissions,MessageActionRow,MessageButton } = require("discord.js");
const { default_prefix ,color,error,owner,xmark,checked } = require("../config.json")
const db = require('quick.db')
const axios = require('axios')
const urlRegex = require('url-regex')
module.exports = {
  event: "messageCreate",
  execute: async (message, client) => {
  //  if (!message.guild) return; console
    if (message.author.bot) return;
 
    
       if(message.type === 'USER_PREMIUM_GUILD_SUBSCRIPTION'){

       let channel = db.get(`boostchan_${message.guild.id}`)
       let welcome = db.get(`boostmsg_${message.guild.id}`)
       
      welcome = welcome.replace('{user}', message.member);
      welcome = welcome.replace('{user.name}', message.author.username);
      welcome = welcome.replace('{user.tag}', message.author.tag);
      welcome = welcome.replace('{user.id}', message.author.id);
      welcome = welcome.replace('{boostcount}', message.guild.premiumSubscriptionCount);
      welcome = welcome.replace('{levelcount}', message.guild.premiumTier.replace('TIER_', '' && 'NONE','0'));
      welcome = welcome.replace('{guild.name}', message.member.guild.name);
      welcome = welcome.replace('{guild.id}', message.member.guild.id);
       if(channel && welcome) client.channels.cache.get(channel).send({embeds:[
       {
         description:welcome,
         color:color
       }
       ]})
   }

      let prefix2 = db.get(`prefix_${message.author.id}`)
      if (prefix2 === null) prefix2 = db.get(`prefix_${message.guild.id}`)
      
    const args1 = message.content.trim().split(/ +/g);
    if (prefix2 === null) { prefix2 = default_prefix; }
    if (args1.length === 1 && message.mentions.users.has(client.user.id)) {
    let mentionedMember =  message.member;
      const prefixEmbed = new MessageEmbed()
        .setDescription(`<:dbot_icon_settings:995777328946892810>  **Prefixes For ${message.author.username}** \n> Default Prefix: \`${default_prefix}\` \n> Server prefix: \`${db.get(`prefix_${message.guild.id}`)}\` \n> Custom Prefix: \`${db.get(`prefix_${message.author.id}` || "Not Set")}\``)
        .setColor(color)  

    //message.reply({embeds:[prefixEmbed]}).catch(() => {/*Ignore error*/})
    }
    if(db.get(`mocklock_${message.author.id}`)) {
    axios.get(`https://luminabot.xyz/api/text/mock?text=${message.content}`)
    .then(response => {

 
 message.channel.send({content:`${response.data.text} **- ${message.author.tag}**`})
 .then(message.delete() )
   return;
    })
    
}

    
     let prefix = db.get(`prefix_${message.author.id}`)
      if (prefix === null) prefix = db.get(`prefix_${message.guild.id}`)
     
    if (prefix === null) prefix = default_prefix;
    if (!message.content.startsWith(message.content.match(new RegExp(`^<@!?(${client.user.id})>`,"gi")) || prefix || default_prefix) || message.author.bot) return;
    const args = message.content.slice(prefix.length).split(/ +/);
    const commandName = args.shift().toLowerCase();
    const command =
      client.commands.get(commandName) ||
      client.commands.find(
        (cmd) => cmd.aliases && cmd.aliases.includes(commandName)
      );
           let embedsf = new MessageEmbed()
      .setDescription(`${xmark} Command not found`)
       .setColor(error)
      
      
    if (!command) return;

    if (command.guildOnly && message.channel.type !== "text") {
    return;
    
    }

    if (command.args && !args.length) {
      if (command.usage) {
      }
      return;
    }
    

    try {
                    let blacklisted = db.get(`blacklisted`)
        if(blacklisted && blacklisted.find(find => find.user == message.author.id)) {
        return;
        }
              let trustedusers = db.get(`privacy`)
        if(trustedusers && trustedusers.find(find => find.user == message.author.id)) {
          let cp = db.get(`commandsused`)
          db.set(`commandsused`,cp + 1)
         // console.log(message.content)
        command.execute(message,args,client)
        .catch(error => {
          message.channel.send({
            embeds:[
              {
                description:`**An error ocurred** \n ${error.message} \n make sure to inform us in discord.gg/heist`,
                color:`F7C91D`
              }
            ]
          })
        })
        }
      else {
                  const row = new MessageActionRow().addComponents(
             new MessageButton()
              .setCustomId('yes')
              .setEmoji("<:Blurple_check:1013176396861931630>")
              .setStyle('SECONDARY'),
            
            new MessageButton()
              .setCustomId('no')
              .setEmoji("<:DW_X_Mark:1013176426763145216>")
              .setStyle('SECONDARY')
          )
          let msg = message.reply({embeds:[
            new MessageEmbed().setDescription(`Do you agree to allstars [Privacy policy](https://nekokouri.gitbook.io/allstar/details/privacy-policy) \n **Warning** Reacting with ${xmark} will blacklist you from using allstar`).setColor(color)
          ],
                         components:[row]
                        })
         // const filter = (i) => {
        //    if(i.author.id === message.author.id) return true
        //  }
          
          const collector = message.channel.createMessageComponentCollector({
            filter: i => i.user.id === message.author.id,
            max:1
          })
          
          collector.on("end", (ButtonInteraction) => {
           
            const id = ButtonInteraction.first().customId;
            if(id === 'yes') {
              
                      let trustedusers = db.get(`privacy`)
        if(trustedusers && trustedusers.find(find => find.user == message.author.id)) {
          let trust = new MessageEmbed()
          .setColor(error)
          .setDescription(`${xmark} That user is already whitelisted`)
        return 
        }
let data = {
    user: message.author.id
}
        db.push(`privacy`, data)
        let added = new MessageEmbed()
        .setDescription(`
       ${checked}  You accepted to allstars privacy policy
        `)
        .setColor(color)

        return message.reply({
            embeds: [added]
        });

              
              
              
              
            }
            if(id === 'no') {
              let data = {
    user: message.author.id
}
              db.push(`blacklisted`,data)
           let embed = new MessageEmbed()
          .setColor(color)
            return message.channel.send({embeds:[
              new MessageEmbed().setDescription(`${xmark} now you'll be blacklisted from using commands`).setColor(color)
            ]})
            }
          })
        
      }


     // command.execute(message,args,client)
       console.log(`Comamnd ran by un authorized user ${message.author.tag} command : ${command.name} Time : ${Date.now()} Server : ${message.guild.name}`)
    

     // command.execute(message, args, client);
    } catch (error) {
    }
  },
};