const db = require('quick.db')
const { MessageEmbed } = require('discord.js')
const { stripIndent} = require('common-tags')
module.exports = async (client) => {
  client.user.setPresence({ status: 'idle' });
  
  for (const guild of client.guilds.cache.values()) {
    const ig = db.get(`instagram_stream_${guild.id}`)
    if (ig) {
      const channel = client.channels.cache.get(ig.channel)
      if (channel) {
        const Insta = require('scraper-instagram');
        const InstaClient = new Insta();
        InstaClient.authBySessionId('5584450039%3Ar5kqVztO7tdFEd%3A23')
        client.logger.info(`Subscribing to Instagram profile: ${ig.user} in ${guild.name}`) 
        InstaClient.subscribeUserPosts(`${ig.user}`, async (post, err) => {
          if (post) {
            post = await InstaClient.getPost(post.shortcode)
            if (post.contents.length && post.contents[0].type === 'photo') {
              const embed = new MessageEmbed()
                .setAuthor(`${post.author.name !== '' ? post.author.name : post.author.username}`, post.author.pic)
                .setTitle(post.author.username + ` ${post.author.verified ? '<:verified:859242659339042836>' : ''}`)
                .setFooter('Instagram', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/1024px-Instagram_icon.png')
                .setURL(`https://instagram.com/p/${post.shortcode}`)
                .setColor("f26b31")
                .setDescription(stripIndent`${post.caption}`)
                .setImage(post.contents[0].url)
                .setTimestamp(new Date(post.timestamp * 1000))
              channel.send({ embeds: [embed] })
            }
            else {
              post = await InstaClient.getPost(post.shortcode)
              const embed = new MessageEmbed()
                .setAuthor(`${post.author.name !== '' ? post.author.name : post.author.username}`, post.author.pic)
                .setTitle(post.author.username + ` ${post.author.verified ? '<:verified:859242659339042836>' : ''}`)
                .setFooter('Instagram', 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/1024px-Instagram_icon.png')
                .setURL(`https://instagram.com/p/${post.shortcode}`)
                .setColor("f26b31")
                .setDescription(stripIndent`${post.caption}`)
                .setTimestamp(new Date(post.timestamp * 1000))
              channel.send({ embeds: [embed], files: [post.contents[0].url] })
            }
          }
        }, {
          interval: 60,
          lastPostShortcode: 'slattnem',
          fullPosts: false,
        })
      }
    }
    const prefix_find = await client.db.prefix.findOne({ where: { guildID: guild.id } })
    if (!prefix_find) {
      await client.db.prefix.create({
        guildID: guild.id,
        prefix: ';'
      })
      client.logger.info(`${guild.name} updated with new prefix`)
    }
  }
  client.logger.info('Slatt is now online');
  client.logger.info(`Slatt is running on ${client.guilds.cache.size} server(s)`);
};