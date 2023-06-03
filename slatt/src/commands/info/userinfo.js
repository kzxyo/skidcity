const Command = require('../Command.js');
const {
  MessageEmbed, DiscordAPIError
} = require('discord.js');
const moment = require('moment');
const Badges = require('../../utils/json/badges.js')
module.exports = class UserInfoCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'userinfo',
      aliases: ['whois', 'user', 'ui'],
      usage: 'userinfo [member | id]',
      description: 'Fetches a user\'s information whether they\'re in the server or not',
      type: client.types.INFO,
      subcommands: ['userinfo @conspiracy']
    });
  }
  async run(message, args) {
    const Discord = require('discord.js')
    message.channel.sendTyping()
    const member = this.functions.get_member_or_self(message, args.join(' '))
    let Flags
      if (member && member.user.flags) {
        Flags = member.user.flags.toArray()
        Flags = Flags.filter(b => !!Badges[b]).map(m => Badges[m].emoji).join(' ')
      }
    if (!member) {
      if (isNaN(args[0])) {
        return this.invalidUser(message)
      }
      message.client.users.fetch(args[0]).then(u => {
        let gs = message.client.guilds.cache.filter(guild => !!guild.members.cache.get(u.id))
        let m = gs.size || '0'
        let {
          snowflake
        } = require('../snowflakeFormatter.js');
        let sf = snowflake(u.id);
        Flags = u.flags.toArray()
        Flags = Flags.filter(b => !!Badges[b]).map(m => Badges[m].emoji).join(' ')
        const embed = new MessageEmbed()
          .setAuthor(u.username + '#' + u.discriminator, `${u.avatar ? `https://cdn.discordapp.com/avatars/${u.id}/${u.avatar}${u.avatar.startsWith('a_') ? '.gif' : '.webp'}` : ''}`)
          .setTitle(u.username)
          .setDescription(`${Flags}`)
          .addField(`**Joined guild**`, `Unkown`, true)
          .addField(`**Created account**`, `${moment(new Date(sf.timestamp)).format('MMM DD YYYY')}`, true)
          .addField(`**Boosted Guild**`, `Unkown`, true)
          .setFooter(`Join position: Unkown · mutual servers: ${m}`)
          .setColor(this.hex)
        message.channel.send({ embeds: [embed] })
      })
      return
    }

    let guilds = message.client.guilds.cache.filter(guild => !!guild.members.cache.get(member.id))
    let mutual = guilds.size
    const jp = message.guild.members.cache.sorted((a, b) => a.joinedAt - b.joinedAt).map(x => x.id).indexOf(member.id) + 1
    let Roles = []
    if (member.roles.cache.size > 10) {
      member.roles.cache.forEach(r => {
        if (Roles.length !== 10) {
          if (r !== message.guild.roles.everyone) Roles.push(`<@&${r.id}>`)

        }
      })
      Roles = Roles.join(', ') + ` and **${member.roles.cache.size - 10}** more`
    } else {
      member.roles.cache.forEach(r => {
        if (r !== message.guild.roles.everyone) Roles.push(`<@&${r.id}>`)
      })
      Roles = Roles.join(', ')
    }
    const {
      LastfmUsers,
    } = require('../../utils/db.js');
    const user = await LastfmUsers.findOne({
      where: {
        userID: member.id
      }
    })
    const activities = [];
    if (user) {
      let recent = await this.lastfm.user_getrecent(user.username)
      if (recent.recenttracks.track.length) {
        let track = recent.recenttracks.track[0] ? recent.recenttracks.track[0].name : '**None**'
        let artist = recent.recenttracks.track[0] ? recent.recenttracks.track[0].artist['#text'] : '**None**'
        let url = recent.recenttracks.track[0] ? recent.recenttracks.track[0].url : '**None**'
        let np
        if (!recent.recenttracks.track[0]['@attr']) np = 'Recently played'
        if (recent.recenttracks.track[0]['@attr']) np = 'Now playing'
        activities.push(`<:lastfm:794723149421871135> ${np} [${track}](${url}) by **${artist}**`)
      }
    }
    if (member.presence) {
      for (const activity of member.presence.activities.values()) {
        switch (activity.type) {
          case 'PLAYING':
            activities.push(`🎮 Playing **${activity.name}**`);
            break;
          case 'LISTENING':
            if (member.user.bot) activities.push(`Listening to **${activity.name}**`);
            else activities.push(`🎵 Listening to **${activity.details}** by **${activity.state}**`);
            break;
          case 'WATCHING':
            activities.push(`📺 Watching **${activity.name}**`);
            break;
          case 'STREAMING':
            activities.push(`<:twitch:827675731793281044> Streaming **${activity.name}**`);
            break;
        }
      }
    }
    let acknowledgment
    if (member.id === message.guild.ownerID) {
      acknowledgment = 'Server Owner'
    } else if (member.permissions.has('ADMINISTRATOR')) {
      acknowledgment = 'Server Administrator'
    } else if (member.permissions.has('MANAGE_CHANNELS')
      || member.permissions.has('MANAGE_MESSAGES')
      || member.permissions.has('BAN_MEMBERS')
      || member.permissions.has('KICK_MEMBERS')
      || member.permissions.has('MANAGE_ROLES')
      || member.permissions.has('MANAGE_GUILD')) {
      acknowledgment = 'Server Moderator'
    } else {
      acknowledgment = 'Server Member'
    }
    let badge = await message.client.db.badge.findOne({ where: { userID: member.id } })
    if (badge) badge = '<:verified:859242659339042836>'
    else badge = ''

    const embed = new MessageEmbed()
      .setAuthor(`${member.user.tag}`, member.user.displayAvatarURL({
        dynamic: true
      }))
      .setTitle(member.user.username + ` ${member.nickname ? `(${member.nickname})` : ''} ${badge === null ? '' : badge}`)
      .setDescription(`${Flags}\n${member.voice.channel ? `> 🔉 Connected to **${member.voice.channel}**` : ''}`)
    if (activities.length) embed.addField(`Activities`, `${activities.join('\n')}`)
    embed.addField(`Joined guild`, `${moment(member.joinedAt).format('MMM DD YYYY')}`, true)
    embed.addField(`Created account`, `${moment(member.user.createdAt).format('MMM DD YYYY')}`, true)
    embed.addField(`Boosted guild`, `${member.premiumSince ? moment(member.premiumSinceTimestamp).format('LLLL') : 'Unknown'}`, true)
    embed.setFooter(`Join Position: ${jp} · mutual servers: ${mutual}`, message.author.displayAvatarURL({
      dynamic: true
    }))
    embed.setColor(this.hex)
    if (Roles.length) embed.addField(`Roles`, `${Roles}`)
    embed.addField(`Acknowledgment`, `${acknowledgment}`)
    message.channel.send({ embeds: [embed] });
  }
}