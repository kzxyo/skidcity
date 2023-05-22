const { MessageEmbed,MessageAttachment,Collection,Client } = require("discord.js");
const { default_prefix ,color,error,owner } = require("../config.json")
const db = require('quick.db')
const ms = require('moment');


module.exports = {
  event: "messageDelete",
  execute: async (message, guild,client,args) => {
    if(message.author.bot)return;
    if(message.content.includes('https://')) return;
    if(message.author.id === '839221856976109608') return;
    //console.log(message.attachments.first().proxyURL)

 if (message.attachments.size > 0) {
 let image = message.attachments.first().proxyURL; 
    if (message.author.bot) return;
  if (message.partial) return

        if (message.author) {
      
      db.push(`snipeindex_${message.channel.id}`, {
        message:{
        content: message.content,
        author: message.author.tag,
        image: message.attachments.first().proxyURL,
        avatar:message.author.displayAvatarURL({dynamic:true})
        }
      })
    }
   setTimeout(()=> {
     db.delete(`snipes_${message.channel.id}`)
   },900000)
  let auto = db.get(`autosniped_${message.guild.id}`);
  if(auto === true) {
   let image = message.attachments.first() ? message.attachments.first().proxyURL : null
    let embed = new MessageEmbed()
    .setAuthor({name:`${message.author.tag}`,iconURL:`${message.author.displayAvatarURL()}`})
     .setDescription(' \```' + message.content + '\``` ')
    .setTimestamp()
    .setColor(message.member.displayHexColor || color)
    .setFooter({text:`Auto-Sniped`})
   .setImage(message.attachments.first().proxyURL)
    message.channel.send({embeds:[embed]})

}
   let chx = db.get(`logs_${message.guild.id}`);
     if(chx) {
   let image = message.attachments.first() ? message.attachments.first().proxyURL : null
    let embed = new MessageEmbed()

     .setDescription(`**Mod Logs** <:allstarmoderation:1032192249754288169>  \n\n <:allstarreply:1032192256192553030> Message Deleted by ${message.author.tag} <:allstarreply:1032192256192553030> \n\n `+' \```' + message.content + '\``` ')

    .setColor(color)
   .setImage(message.attachments.first().proxyURL)
    message.guild.channels.cache.get(chx).send({embeds:[embed]})

}
   
 } else {
     if (message.partial) return
    if(message.content.includes('https://')) return;
        if (message.author) {
          db.push(`snipeindex_${message.channel.id}`, {
            message:{
            content: message.content,
            author: message.author.tag,
            avatar:message.author.displayAvatarURL({dynamic:true})
            }
          })
             setTimeout(()=> {
     db.delete(`snipes_${message.channel.id}`)
   },900000)
    }
  let auto = db.get(`autosniped_${message.guild.id}`);
  if(auto === true) {
   let image = message.attachments.first() ? message.attachments.first().proxyURL : null
    let embed = new MessageEmbed()
    .setAuthor({name:`${message.author.tag}`,iconURL:`${message.author.displayAvatarURL()}`})
          .setDescription(' \```' + message.content + '\``` ')
    .setTimestamp()
    .setFooter({text:`Auto-Sniped`})
    .setColor(message.member.displayHexColor || color)
    message.channel.send({embeds:[embed]})
  }
  let chx = db.get(`logs_${message.guild.id}`);
     if(chx) {
   let image = message.attachments.first() ? message.attachments.first().proxyURL : null
    let embed = new MessageEmbed()
     .setDescription(`**Mod Logs** <:allstarmoderation:1032192249754288169>  \n\n <:allstarreply:1032192256192553030> Message Deleted by ${message.author.tag} <:allstarreply:1032192256192553030> \n\n `+' \```' + message.content + '\``` ')
   

    .setColor(color)
    message.guild.channels.cache.get(chx).send({embeds:[embed]})
  }
 }
    
  },
};

