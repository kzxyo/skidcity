const Discord = require('discord.js');
const { stripIndents } = require("common-tags");
const urban = require('urban');
const { color } = require("../../config.json");

module.exports = {
  name: "urbandictionary",
  aliases: ["ud", "urban", "define"],

run: async(client, message, args) => {

  let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!mentionedMember) mentionedMember = message.member;

  const urbanEmbed = new Discord.MessageEmbed()
  .setAuthor(message.author.username, message.author.avatarURL({
    dynamic: true
  }))
  .setTitle('Command: urbandictionary')
  .setDescription('Gets the definition of a word/slang from Urbandictionary')
  .addField('**Aliases**', 'define, ud, urban', true)
  .addField('**Parameters**', 'search', true)
  .addField('**Information**', `N/A`, true)
  .addField('**Usage**', '\`\`\`Syntax: urbandictionary <word>\nExample: urbandictionary Slatt\`\`\`')
  .setFooter(`Module: fun`)
  .setTimestamp()
  .setColor(color)
if(!args[0]) return message.channel.send(urbanEmbed);
      
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
        .setAuthor(message.author.username, message.author.avatarURL({
          dynamic: true
        }))
        .setTitle(`**${word}**`)
        .setURL(`${permalink || 'https://www.urbandictionary.com/'}`)
        .setDescription(stripIndents`${definition || 'No Definition'}
        **Example**\n${example || 'No Example'}`)
        .setTimestamp()
        .addField(`**Votes**`, `👍 \`${thumbs_up} / ${thumbs_down}\` 👎`)
        .setFooter(`Urban Dictionary Results`, img);
      
      message.channel.send(embed);
    });
  } catch(e){
  
    
    return message.channel.send(`Error, try again (${e})`);
  }
}
}