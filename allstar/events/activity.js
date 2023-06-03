const { MessageEmbed } = require("discord.js");

const { default_prefix ,color,error,owner,xmark } = require("../config.json")
const db = require('quick.db')
module.exports = {
  event: "messageCreate",
  execute: async (message, client) => {
    
      if (message.author.bot) return;
     if (message.partial) return
          let blacklisted = db.get(`blacklisted`)
        if(blacklisted && blacklisted.find(find => find.user == message.author.id)) {
        return;
        }
    let ds = db.get(`activity_${message.guild.id}_${message.author.id}`)

      db.set(`activity_${message.guild.id}_${message.author.id}`,ds + 1)
    

    
    
  },
};