const config = require('../../config.json')
const fetch = require('node-fetch')
const { MessageEmbed } = require('discord.js')
const { color } = require("../../config.json");

module.exports = {
  name: "userbanner",
  aliases: ['ub'],

  run: async (client, message, args) => {
    message.channel.startTyping();
    let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || args[0] || message.member;

    const user = await client.users.fetch(client.users.resolveID(mentionedMember)).catch(() => null);
    if (!user) user = message.author;
    let uid = user.id
    let response = fetch(`https://discord.com/api/v8/users/${uid}`, {
      method: 'GET',
      headers: {
        Authorization: `Bot ${config.token}`
      }
    })
    let receive = ''
    let banner = 'https://cdn.discordapp.com/attachments/829722741288337428/834016013678673950/banner_invisible.gif'
    response.then(a => {
      if (a.status !== 404) {
        a.json().then(data => {
          receive = data['banner']
          if (receive !== null) {
            let response2 = fetch(`https://cdn.discordapp.com/banners/${uid}/${receive}.gif`, {
              method: 'GET',
              headers: {
                Authorization: `Bot ${config.token}`
              }
            })
            let statut = ''
            response2.then(b => {
              statut = b.status
              banner = `https://cdn.discordapp.com/banners/${uid}/${receive}.gif?size=1024`
              if (statut === 415) {
                banner = `https://cdn.discordapp.com/banners/${uid}/${receive}.png?size=1024`
              }
            })
          }
        })
      }
    })
    setTimeout(() => {
      let embed = new MessageEmbed()
        .setColor(mentionedMember.displayHexColor || color)
        .setImage(banner)
        .setURL(banner)
        .setAuthor(message.author.username, message.author.avatarURL())
        .setTitle(user.username + "'s banner")
      message.channel.stopTyping(true);
      message.channel.send(embed)
    }, 1000)
  }
}
