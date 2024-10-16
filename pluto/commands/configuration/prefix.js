const { Permissions } = require("discord.js");
const { prefix } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "prefix",
  aliases: ['setprefix', 'plutoprefix'],
  description: `change the guild prefix`,
  usage: '{guildprefix}prefix [prefix]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_GUILD)) return message.channel.send(`this command requires \`manage server\` permission`)

    const prefixname = args[0]

    if (!prefixname) return message.channel.send(`my current prefix is \`${guildprefix}\``)

    if(args[0].length > 3) return message.channel.send('prefix cant be over 3 letters')    

    if(args[1]) return message.channel.send('cant have a spaced prefix')
    
    if (globaldata.Prefix) {

      globaldata.Prefix = prefixname;
  
      await globaldata.save();
  
      return message.channel.send(`my prefix has been changed to \`${prefixname}\``)   
    }
  }
}