const { MessageEmbed } = require("discord.js");
const { default_prefix ,color,error,owner,xmark } = require("../config.json")
const db = require('quick.db')
module.exports = {
  event: "messageCreate",
  execute: async (message, client) => {
    
    
let antilink =  db.get(`antilink_${message.guild.id}`);
if(antilink !== true) return
      if(message.author.id === client.user.id) return;
      if(message.author.id === message.guild.ownerId) return;
         let trustedusers = db.get(`linktrusted_${message.guild.id}`)
          if(trustedusers && trustedusers.find(find => find.user == message.author.id)) {
          return;
          }
let filtered = [
  "http://",
  "https://"
]      

try {
  if(message.content.includes('https://')){
   
  message.delete()
  message.channel.send({embeds:[{description:`${xmark} ${message.author.tag} You are not allowed to send links `,color:error}]})
  }
 if(message.content.includes('http://')) {
  
      message.delete()
  message.channel.send({embeds:[{description:`${xmark} ${message.author.tag} You are not allowed to send links `,color:error}]})
  }
}catch{
  
}
      
    
  },
};