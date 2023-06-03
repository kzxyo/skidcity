const Discord = require('discord.js');
const { stripIndents } = require('common-tags');
const twitter = require('twitter-api.js');
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
  name: "twitter",
  aliases: ['twit'],

  run: async (client, message, args) => {
    let user = args[0];
    const twitterEmbed = new Discord.MessageEmbed()
    .setAuthor(message.author.username, message.author.avatarURL({
      dynamic: true
    }))
    .setTitle('Command: twitter')
    .setDescription('Check a twitter account profile')
    .addField('**Aliases**', 'twit', true)
    .addField('**Parameters**', 'handle', true)
    .addField('**Information**', `N/A`, true)
    .addField('**Usage**', '\`\`\`Syntax: twitter (subcommand) <args>\nExample: twitter @fourr\`\`\`')
    .setFooter(`Module: information`)
    .setTimestamp()
    .setColor(color)
    if (!args[0]) return message.channel.send(twitterEmbed)

    try {
      const body = await twitter.users(user);
      const tweet = new Discord.MessageEmbed()
        .setColor('BLUE')
        .setURL(`https://twitter.com/${body.screen_name}`)
        .setAuthor(`${message.author.username}`, message.author.displayAvatarURL({
          dynamic: true,
          size: 2048
        }))
        .setTitle(
          `${body.name} (@${body.screen_name.toLocaleString()})`,
          body.verified
            ? 'https://emoji.gg/assets/emoji/6817_Discord_Verified.png'
            : null
        )
        .setDescription(
          stripIndents` ${body.description}`)
        .setFooter(
          `Twitter ID: ${body.id}`,
          'https://abs.twimg.com/favicons/twitter.ico'
        )
        .setThumbnail(body.profile_image_url_https.replace('_normal', ''))
        .addFields(
          {
            name: "**Tweets**",
            value: `${body.statuses_count.toLocaleString()}`,
            inline: true
          },
          {
            name: "**Following**",
            value: `${body.friends_count.toLocaleString()}`,
            inline: true,
          },
          {
            name: "**Followers**",
            value: `${body.followers_count.toLocaleString()}`,
            inline: true,
          }
        )

      message.channel.send(tweet);
    } catch (e) {
      if (e.status === 403)
        return message.channel.send(
          { embed: {color: "#efa23a", description: `${warn} ${message.author}: That user is either **suspended** or is on **private mode**`}}
        );
      else if (e.status === 404) return message.channel.send({ embed: {color: "#efa23a", description: `${warn} ${message.author}: That **user** doesn't exist`}});
      else return message.channel.send(`**Unknown Error:** \`${e.message}\``);
    }
  }
};