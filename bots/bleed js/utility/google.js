const Discord = require('discord.js');
const google = require('google');
const { color } = require("../../config.json");

module.exports = {
  name: "google",
  aliases: ["g"],
  category: "utility",

  run: async (client, message, args) => {
    let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!mentionedMember) mentionedMember = message.member;

    message.channel.startTyping();
    google.resultsPerPage = 3;

    google(args.join("+"), function (err, res) {
      if (err) message.channel.send({ embed: { color: "#6495ED", description: `:mag_right: ${message.author}: No results found were found for **${args.join(' ')}**` } });

      let link = res.links[0];
      let googleIcon = 'https://maxcdn.icons8.com/Share/icon/Logos//google_logo1600.png';

      const embed = new Discord.MessageEmbed()
        .setColor(mentionedMember.displayHexColor || color)
        .setAuthor(`${message.author.username}`, message.author.displayAvatarURL({
          dynamic: true,
          size: 2048
        }))
        .setTitle(`Search Results for ${args.join(' ')}`)
        .setFooter(googleIcon)
        .addField(`**${link.title} - ${link.href}**`, link.description)

      message.channel.stopTyping(true);
      message.channel.sendEmbed(embed).catch(e => {
        message.channel.sendMessage("There was an error!\n" + e);
      });
    });
  }
}
