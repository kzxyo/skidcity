const { MessageEmbed, Permissions } = require("discord.js");
const db = require('quick.db')
const {
  default_prefix,
  color,
  error,
  owner,
  checked,
  xmark,
} = require("../config.json");
const talkedRecently = new Set();
module.exports = {
  name: "antinuke",
  description: "antinuke events/configs/info",
  aliases: ["an"],
  usage: "  ```YAML\n\n antinuke [on/off] \n antinuke settings \n antinuke info \n antinuke settings \n antinuke enable {event_nane}``` ",
  category: "security",
  guildOnly: false,
  args: false,
  permissions: {
    bot: [],
    user: [],
  },
  execute: async (message, args, client) => {
    let emoji = `<:887705796476018688:989122635705233418> `;
    if (talkedRecently.has(message.author.id)) {
      message.react(`⌛`);
    } else {
      let vanity = db.get(`vanity_${message.guild.id}`);
      let checkenable = new MessageEmbed()
        .setAuthor({ name: "Security" })
        .setDescription(
          `<:allstarenabled:996521189986021386> Antinuke Is Enabled VanityURL - ${vanity} \n Usage : \n <:allstar:1001031487103193108> whitelist <<heist#0001> \n <:allstar:1001031487103193108> blacklist <<heist#0001>> \n <:allstar:1001031487103193108> antinuke [on/off] \n <:allstar:1001031487103193108> antinuke info \n <:allstar:1001031487103193108> antinuke settings \n <:allstar:1001031487103193108> antinuke enable antiban `
        )
        .setThumbnail(
          `https://cdn.discordapp.com/attachments/991601306747813978/996704762110148688/IconServerSecurity_1.gif`
        )
        .setColor(color);
      let checkdisabled = new MessageEmbed()
        .setDescription(
          `<:allstardisabled:996521221749481516>  Antinuke Is Disabled \n Usage : \n <:allstar:1001031487103193108> whitelist <<heist#0001> \n <:allstar:1001031487103193108> blacklist <<heist#0001>> \n <:allstar:1001031487103193108> antinuke [on/off] \n <:allstar:1001031487103193108> antinuke info \n <:allstar:1001031487103193108> antinuke settings \n <:allstar:1001031487103193108> antinuke enable antiban `
        )
        .setThumbnail(
          `https://cdn.discordapp.com/attachments/991601306747813978/996704762110148688/IconServerSecurity_1.gif`
        )
        .setColor(color);
      let onlyown = new MessageEmbed()
        .setDescription(`${xmark} Only server owner can use this command`)
        .setColor(error);

      const authorized = [message.guild.ownerId, owner];
      //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
      if (!authorized.includes(message.author.id))
        return message.reply({ embeds: [onlyown] }).catch(() => {
          /*Ignore error*/
        });

      let aenabled = new MessageEmbed()
        .setDescription(`${checked} Antinuke is now enabled`)
        .setColor(color);
      let missperms = new MessageEmbed()
        .setDescription(`${xmark}  You're missing \`MANAGE_GUILD\` permission`)
        .setColor(error);

      let nukeable = new MessageEmbed()
        .setDescription(`${checked} Antinuke Enabled`)
        .setColor(color);
      if (args[0] == "on") {
        if (!authorized.includes(message.author.id))
          return message.reply({ embeds: [onlyown] });
        if ((await db.has(`anti-new_${message.guild.id}`)) === false) {
          await db.set(`anti-new_${message.guild.id}`, true)
                    db.set(`antiguildupdate_${message.guild.id}`,true)

          db.set(`antiwebhookdelete_${message.guild.id}`,true)
          db.set(`antichannelcreate_${message.guild.id}`,true)
          
          db.set(`antichanneldelete_${message.guild.id}`,true)

          db.set(`antichannelupdate_${message.guild.id}`,true)

          db.set(`antiban_${message.guild.id}`,true)

          db.set(`antikick_${message.guild.id}`,true)

          db.set(`antibotadd_${message.guild.id}`,true)

          db.set(`antikick_${message.guild.id}`,true)

          db.set(`antirolecreate_${message.guild.id}`,true)

          db.set(`antiroledelete_${message.guild.id}`,true)

          db.set(`antiroleupdate_${message.guild.id}`,true)

          db.set(`antirolemember_${message.guild.id}`,true)

          db.set(`antiwebhookcreate_${message.guild.id}`,true)
  
          db.set(`antiwebhookdelete_${message.guild.id}`,true)

          db.set(`antiwebhookupdate_${message.guild.id}`,true)
          message
            .reply({
              embeds: [nukeable],
              content: `**Whitelist all trusted admins**`,
            })
            .catch(() => {
              /*Ignore error*/
            });
        } else
          return message.reply({ embeds: [aenabled] }).catch(() => {
            /*Ignore error*/
          });
      } else if (args[0] == "off") {
        db.delete(`trustedusers_${message.guild.id}`);
                   db.delete(`antiguildupdate_${message.guild.id}`)
  
          db.delete(`antichannelcreate_${message.guild.id}`)
          
          db.delete(`antichanneldelete_${message.guild.id}`)
     
          db.delete(`antichannelupdate_${message.guild.id}`)
  
          db.delete(`antiban_${message.guild.id}`)
      
          db.delete(`antikick_${message.guild.id}`)
        
          db.delete(`antibotadd_${message.guild.id}`)
    
          db.delete(`antikick_${message.guild.id}`) 
      
          db.delete(`antirolecreate_${message.guild.id}`)
      
          db.delete(`antiroledelete_${message.guild.id}`)
      
          db.delete(`antiroleupdate_${message.guild.id}`)
      
          db.delete(`antirolemember_${message.guild.id}`)
 
          db.delete(`antiwebhookcreate_${message.guild.id}`)
     
          db.delete(`antiwebhookdelete_${message.guild.id}`)
    
          db.delete(`antiwebhookupdate_${message.guild.id}`)
        let disabled = new MessageEmbed()
          .setDescription(`${checked}  Antinuke is now disabled`)
          .setColor(color);
        let alreadydisabled = new MessageEmbed()
          .setDescription(`${xmark}  Antinuke is disabled`)
          .setColor(error);
        if ((await db.has(`anti-new_${message.guild.id}`)) === true) {
          await db.delete(`anti-new_${message.guild.id}`);
          message.reply({ embeds: [disabled] }).catch(() => {
            /*Ignore error*/
          });
        } else
          return message.reply({ embeds: [alreadydisabled] }).catch(() => {
            /*Ignore error*/
          });
      }
      if (!args[0]) {
        let antinuke = db.get(`anti-new_${message.guild.id}`);
        if (antinuke !== true) {
          return message.reply({ embeds: [checkdisabled] }).catch(() => {
            /*Ignore error*/
          });
        } else if (antinuke === true) {
          return message.reply({ embeds: [checkenable] }).catch(() => {
            /*Ignore error*/
          });
        }
      } else if (args[0] == "info") {
        let embed11 = new MessageEmbed()
          .setTitle(
            `<:allstarsecurity:996512639666618518>  Allstar Antinuke To keep your server safe`
          )
          .addField(
            `Anti Features :`,
            ` <:allstar:1001031487103193108> Vanity Update \n <:allstar:1001031487103193108> Channel Create \n <:allstar:1001031487103193108> Channel Delete \n <:allstar:1001031487103193108> Channel Update \n <:allstar:1001031487103193108> Ban Add \n <:allstar:1001031487103193108> Bot Add \n <:allstar:1001031487103193108> Kick Add \n <:allstar:1001031487103193108> Role Create \n <:allstar:1001031487103193108> Role Delete \n <:allstar:1001031487103193108> Role Update \n <:allstar:1001031487103193108> Role Member \n<:allstar:1001031487103193108> Webhook Create \n <:allstar:1001031487103193108> Webhook Delete \n <:allstar:1001031487103193108> Webhook Update`
          )
          .setThumbnail(client.user.displayAvatarURL())
          .setColor(color);

        message.reply({ embeds: [embed11] }).catch(() => {
          /*Ignore error*/
        });
      }else if(args[0] == 'enable'){
               let enbla = db.get(`anti-new_${message.guild.id}`)

       if(enbla!== true) {return message.reply({embeds:[{description:`${xmark} You need to enable antinuke first.`,color:error}]}) } 
        if(args[1] == 'antiguildupdate'){
          db.set(`antiguildupdate_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antichannelcreate'){
          db.set(`antichannelcreate_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antichanneldelete'){
          db.set(`antichanneldelete_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antichannelupdate'){
          db.set(`antichannelupdate_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiban'){
          db.set(`antiban_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antikick'){
          db.set(`antikick_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antibotadd'){
          db.set(`antibotadd_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antikick'){
          db.set(`antikick_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antirolecreate'){
          db.set(`antirolecreate_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiroledelete'){
          db.set(`antiroledelete_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiroleupdate'){
          db.set(`antiroleupdate_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antirolemember'){
          db.set(`antirolemember_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiwebhookcreate'){
          db.set(`antiwebhookcreate_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiwebhookdelete'){
          db.set(`antiwebhookdelete_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiwebhookupdate'){
          db.set(`antiwebhookupdate_${message.guild.id}`,true)
          message.react(`<:down2:1010942456562462750> `)
        }
        
      }else if(args[0] == 'disable'){
                       let enbla = db.get(`anti-new_${message.guild.id}`)

       if(enbla!== true) {return message.reply({embeds:[{description:`${xmark} You need to enable antinuke first.`,color:error}]}) } 
        if(args[1] == 'antiguildupdate'){
          db.delete(`antiguildupdate_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antichannelcreate'){
          db.delete(`antichannelcreate_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
          
        }else if(args[1] == 'antichanneldelete'){
          db.delete(`antichanneldelete_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antichannelupdate'){
          db.delete(`antichannelupdate_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiban'){ //
          db.delete(`antiban_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antikick'){
          db.delete(`antikick_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antibotadd'){
          db.delete(`antibotadd_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antikick'){
          db.delete(`antikick_${message.guild.id}`) //
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antirolecreate'){
          db.delete(`antirolecreate_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiroledelete'){
          db.delete(`antiroledelete_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiroleupdate'){
          db.delete(`antiroleupdate_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antirolemember'){
          db.delete(`antirolemember_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiwebhookcreate'){
          db.delete(`antiwebhookcreate_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiwebhookdelete'){
          db.delete(`antiwebhookdelete_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }else if(args[1] == 'antiwebhookupdate'){
          db.delete(`antiwebhookupdate_${message.guild.id}`)
          message.react(`<:down2:1010942456562462750> `)
        }
        
      }else if(args[0] == 'settings'){
                       let enbla = db.get(`anti-new_${message.guild.id}`)

       if(enbla!== true) {return message.reply({embeds:[{description:`${xmark} You need to enable antinuke first.`,color:error}]}) } 
                let antibotadd = db.get(`antibotadd_${message.guild.id}`) //done
        if(antibotadd == true)  antibotadd = `<:allstarenabled:1032192242884038676> ` 
        else antibotadd = `<:allstardisabled:1032192240027697193>  `
        
        
        let antiguild = db.get(`antiguildupdate_${message.guild.id}`)
        if(antiguild == true)  antiguild = `<:allstarenabled:1032192242884038676>  ` 
        else antiguild = `<:allstardisabled:1032192240027697193>  `
        
        let antichannelcreate = db.get(`antichannelcreate_${message.guild.id}`)//done
        if(antichannelcreate == true)  antichannelcreate = `<:allstarenabled:1032192242884038676>  ` 
        else antichannelcreate = `<:allstardisabled:1032192240027697193>  `
        
        let antichanneldelete = db.get(`antichanneldelete_${message.guild.id}`)//done
        if(antichanneldelete == true)  antichanneldelete = `<:allstarenabled:1032192242884038676>  ` 
        else antichanneldelete = `<:allstardisabled:1032192240027697193>  `
        
        let antichannelupdate = db.get(`antichannelupdate_${message.guild.id}`)//done
        if(antichannelupdate == true)  antichannelupdate = `<:allstarenabled:1032192242884038676>  ` 
        else antichannelupdate = `<:allstardisabled:1032192240027697193>  `
                
        let antiban = db.get(`antiban_${message.guild.id}`) //done
        if(antiban == true)  antiban = `<:allstarenabled:1032192242884038676>  ` 
        else antiban = `<:allstardisabled:1032192240027697193>  `
                
        let antikick = db.get(`antikick_${message.guild.id}`)//done
        if(antikick == true)  antikick = `<:allstarenabled:1032192242884038676>  ` 
        else antikick = `<:allstardisabled:1032192240027697193>  `
                
        let antirolecreate = db.get(`antirolecreate_${message.guild.id}`)//done
        if(antirolecreate == true)  antirolecreate = `<:allstarenabled:1032192242884038676>  ` 
        else antirolecreate = `<:allstardisabled:1032192240027697193>  `
                
        let antiroledelete = db.get(`antiroledelete_${message.guild.id}`)//done
        if(antiroledelete == true)  antiroledelete = `<:allstarenabled:1032192242884038676>  ` 
        else antiroledelete = `<:allstardisabled:1032192240027697193>  `
                
        let antiroleupdate = db.get(`antiroleupdate_${message.guild.id}`)//done
        if(antiroleupdate == true)  antiroleupdate = `<:allstarenabled:1032192242884038676>  ` 
        else antiroleupdate = `<:allstardisabled:1032192240027697193>  `
                        
        let antirolemember = db.get(`antirolemember_${message.guild.id}`)//done
        if(antirolemember == true)  antirolemember = `<:allstarenabled:1032192242884038676>  ` 
        else antirolemember = `<:allstardisabled:1032192240027697193>  `
                        
        let antiwebhookcreate = db.get(`antiwebhookcreate_${message.guild.id}`)//done
        if(antiwebhookcreate == true)  antiwebhookcreate = `<:allstarenabled:1032192242884038676>  ` 
        else antiwebhookcreate = `<:allstardisabled:1032192240027697193>  `
                        
        let antiwebhookdelete = db.get(`antiwebhookdelete_${message.guild.id}`)//done
        if(antiwebhookdelete == true)  antiwebhookdelete = `<:allstarenabled:1032192242884038676>  ` 
        else antiwebhookdelete = `<:allstardisabled:1032192240027697193>  `
                        
        let antiwebhookupdate = db.get(`antiwebhookupdate_${message.guild.id}`)//done
        if(antiwebhookupdate == true)  antiwebhookupdate = `<:allstarenabled:1032192242884038676>  ` 
        else antiwebhookupdate = `<:allstardisabled:1032192240027697193>  `
        
        let antilink =  db.get(`antilink_${message.guild.id}`);
        if(antilink == true)  antilink = `<:allstarenabled:1032192242884038676>  ` 
        else antilink = `<:allstardisabled:1032192240027697193>  `
        
        let antialt = await db.get(`antiraid_${message.guild.id}`);
        if(antialt  == true) antialt  = `<:allstarenabled:1032192242884038676>  ` 
        else antialt = `<:allstardisabled:1032192240027697193> `
        
        let embed = new MessageEmbed()
        //.setAuthor({name:`     Allstar Antinuke Settings`,iconURL:`${client.user.displayAvatarURL({dynamic:true})}`})
       //.setTitle(`：             Allstar Antinuke Setting              ：`)
        .setDescription('\```' + `             Allstar Antinuke Setting              ` + '\```')
        .addFields(
          {
            name:`Anti Guild Update`,
            value:`<:allstarreply:1001104889432256552> Status ${antiguild} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antiguildupdate`,
            inline:true
          },
          {
            name:`Anti Channel Create`,
            value:`<:allstarreply:1001104889432256552> Status ${antichannelcreate} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antichannelcreate`,
            inline:true
          },
          {
            name:`Anti Channel Delete`,
            value:`<:allstarreply:1001104889432256552> Status ${antichanneldelete} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antichanneldelete`,
            inline:true
          },
          {
            name:`Anti Channel Update`,
            value:`<:allstarreply:1001104889432256552> Status ${antichannelupdate} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antichannelupdate`,
            inline:true
          },
          {
            name:`Anti Ban`,
            value:`<:allstarreply:1001104889432256552> Status ${antiban} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antibann`,
            inline:true
          },
          {
            name:`Anti Bot Add`,
            value:`<:allstarreply:1001104889432256552> Status ${antibotadd} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antibotadd`,
            inline:true
          },
          {
            name:`Anti Kick`,
            value:`<:allstarreply:1001104889432256552> Status ${antikick} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antikick`,
            inline:true
          },
          {
            name:`Anti Role Create`,
            value:`<:allstarreply:1001104889432256552> Status ${antirolecreate} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antirolecreate`,
            inline:true
          },
          {
            name:`Anti Role Delete`,
            value:`<:allstarreply:1001104889432256552> Status ${antiroledelete} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antirolecreate`,
            inline:true
          },
          {
            name:`Anti Role Update`,
            value:`<:allstarreply:1001104889432256552> Status ${antiroleupdate} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antiroleupdate`,
            inline:true
          },
          {
            name:`Anti Role Members`,
            value:`<:allstarreply:1001104889432256552> Status ${antirolemember} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antirolemember`,
            inline:true
          },
          {
            name:`Anti Webhook Create`,
            value:`<:allstarreply:1001104889432256552> Status ${antiwebhookcreate} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antiwebhookcreate`,
            inline:true
          },
          {
            name:`Anti Webhook Delete`,
            value:`<:allstarreply:1001104889432256552> Status ${antiwebhookdelete} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antiwebhookdelete`,
            inline:true
          },
          {
            name:`Anti Webhook Update`,
            value:`<:allstarreply:1001104889432256552> Status ${antiwebhookupdate} \n <:allstarreply:1001104889432256552> Usage : ,antinuke [enable/disable] antiwebhookupdate`,
            inline:true
          },
          {
            name:`Anti Alt Account`,
            value:`<:allstarreply:1001104889432256552> Status ${antialt} \n <:allstarreply:1001104889432256552> Usage : ,antialt [on/off]`,
            inline:true
          },
          {
            name:`Anti Link`,
            value:`<:allstarreply:1001104889432256552> Status ${antilink} \n <:allstarreply:1001104889432256552> Usage : ,antilink [on/off]`,
            inline:true
          }
        )
        .setThumbnail(client.user.displayAvatarURL({dynamic:true,size:4096}))
        .setColor(color)
        message.reply({embeds:[embed]})
      }
      
      
    }

    talkedRecently.add(message.author.id);
    setTimeout(() => {
      // Removes the user from the set after a minute
      talkedRecently.delete(message.author.id);
    }, 3500);
  },
};
