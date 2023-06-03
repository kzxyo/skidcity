const { MessageEmbed } = require('discord.js')
const AppleStore = require('app-store-scraper')
const Discord = require('discord.js');
const { color } = require("../../config.json");

module.exports = {
  name: 'appstore',

  run: async (client, message, args) => {
    let mentionedMember = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!mentionedMember) mentionedMember = message.member;

    const appStoreEmbed = new Discord.MessageEmbed()
    .setAuthor(message.author.username, message.author.avatarURL({
      dynamic: true
    }))
    .setTitle('Command: appstore')
    .setDescription('Search an app on the appstore')
    .addField('**Aliases**', 'N/A', true)
    .addField('**Parameters**', 'search', true)
    .addField('**Information**', `N/A`, true)
    .addField('**Usage**', '\`\`\`Syntax: appstore <query>\nExample: appstore Discord\`\`\`')
    .setFooter(`Module: fun`)
    .setTimestamp()
    .setColor(color)
  if (!args[0]) return message.channel.send(appStoreEmbed)

    let img = 'https://cdn4.iconfinder.com/data/icons/miu-black-social-2/60/app_store-512.png'

    AppleStore.search({
      term: args.join(' '),
      num: 1,
    }).then((data) => {
      let AppInfo

      try {
        AppInfo = JSON.parse(JSON.stringify(data[0]))
      } catch (error) {
        return message.channel.send(`No App With Name **${appname}** Found`)
      }

      let description = AppInfo.description.length > 200 ? `${AppInfo.description.substr(0, 200)}...` : AppInfo.description
      let price = AppInfo.free ? 'Free' : `$${AppInfo.price}`
      let rating = AppInfo.score.toFixed(1)

      const embed = new MessageEmbed()
        .setAuthor(message.author.username, message.author.avatarURL({
          dynamic: true
        }))
        .setTitle(`**${AppInfo.title}**`)
        .setThumbnail(AppInfo.icon)
        .setURL(AppInfo.url)
        .setTimestamp()
        .setColor(mentionedMember.displayHexColor || color)
        .setDescription(description)
        .addField(`**Price**`, price, true)
        .addField(`**Developer**`, AppInfo.developer, true)
        .addField(`**Rating**`, rating, true)
        .setFooter(`App Store Results`, img)
      message.channel.send(embed)
    })
  }
}