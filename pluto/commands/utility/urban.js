const Discord = require('discord.js');
const { stripIndents } = require("common-tags");
const urban = require('urban');
const { color } = require("./../../config.json");
const globaldataschema = require('../../database/global')

module.exports = {
  name: "urbandictionary",
  aliases: ["ub", "urban", "define"],

run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

  let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!mentionedMember) mentionedMember = message.member;

  const urbanEmbed = new Discord.MessageEmbed()
  .setColor(color)
  .setTitle(`${guildprefix}urban`)
  .setDescription('gets the definition of a word/slang from Urbandictionary')
  .addFields(
  { name: '**usage**', value: `${guildprefix}urban [word]\n${guildprefix}ban slatt`, inline: false },
  { name: '**aliases**', value: `ub, urbandictionary, define`, inline: false },
  )
if(!args[0]) return message.channel.send({embeds: [urbanEmbed]});
      
const img = 'https://images-ext-1.discordapp.net/external/8j3tp5o_0hOhrVP_IWHZJcnpmsZ4hdEaNcyEeRCp8TQ/%3Fcache-bust-this-di/https/cdn.notsobot.com/brands/urban-dictionary.png';

  
  let msg = args.slice(0).join(' ');


  let search = urban(msg);
  
  
  try{
    search.first(result => {
      
      if(!result) return message.channel.send('No results found');

      //get info from the result
      let { word, definition, example, thumbs_up, thumbs_down, permalink, author } = result;

      
      let embed = new Discord.MessageEmbed()
        .setColor(mentionedMember.displayHexColor || color)
        .setTitle(`**${word}**`)
        .setURL(`${permalink || 'https://www.urbandictionary.com/'}`)
        .setDescription(stripIndents`${definition || 'No Definition'}
        **Example**\n${example || 'No Example'}`)
        .setTimestamp()
        .addField(`**Votes**`, `👍 \`${thumbs_up} / ${thumbs_down}\` 👎`)
      
      message.channel.send({embeds: [embed]});
    });
  } catch(e){
  
    
    return message.channel.send(`Error, try again (${e})`);
  }
}
}