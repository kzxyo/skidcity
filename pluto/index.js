const { Client, Collection, MessageEmbed, Permissions } = require('discord.js')
const client = new Client({ 
  intents: 32767,
  allowedMentions: { parse: ['users', 'roles'] },
  partials: ['Message', 'Channel', 'Reaction']
})
const { mongooseconnection, prefix, embedcolor, token } = require('./config.json')

client.commands = new Collection();
client.aliases = new Collection();
client.snipes = new Map();
client.editsnipes = new Map();
const cooldowns = new Collection();

['commands'].forEach(handler => {
  require(`./utils/${handler}`)(client);
});

const mongoose = require('mongoose')
const globaldataschema = require('./database/global')
const autoresponderschema = require('./database/autoresponder')
const autoroleschema = require('./database/autorole')
const afkschema = require('./database/afk')
const { EmbedBuilder } = require('./utils/embedbuilder')

//
client.on('ready', async () => {

  console.log(`${client.user.username} is online!`)
  
  client.user.setActivity('soon', {
    type: 'COMPETING'
  })

  if (!mongooseconnection) return;
  
  mongoose.connect(mongooseconnection, {
    useUnifiedTopology: true,
  })

  const guild = client.guilds.cache.get('828746399255887904')

  guild.leave()
})

//
client.on('guildCreate', async (guild) => {

  const logchannel = client.channels.cache.get('1296036418711195762')

    let newdata = new globaldataschema({
      GuildID: guild.id,
      Prefix: prefix,
      BlacklistedUsers: [],
      AntiNukeToggle: null,
      AntiNukeChannel: null,
      AntiNukeWhitelistedUsers: [],
      AntiNukeWhitelistedRoles: [],
      WelcomeMessage: '{user.mention} has joined the server',
      WelcomeChannel: null,
      GoodbyeMessage: '{user.mention} has left the server',
      GoodbyeChannel: null,
      AutoRoles: [],
      JoinDM: null,
      Vanity: null,
      VanityMessage: null,
      VanityRoles: [],
      VanityLogChannel: null
    });

    newdata.save();

    const embed = new MessageEmbed()

    .setColor(embedcolor)
    .setTitle('join guild')
    .setDescription(`name: **${guild.name}** | owner: <@${guild.ownerId}> | id: **${guild.id}** | membercount: **${guild.memberCount}**`)
    .setFooter({ text: `we're now at ${client.guilds.cache.size} servers` })

  logchannel.send({ embeds: [embed] })
})

//
client.on('guildDelete', async (guild) => {

  const logchannel = client.channels.cache.get('1296036418711195762')

  const globaldata = await globaldataschema.findOne({ GuildID: guild.id })

  if (globaldata) {
    await globaldataschema.findOneAndRemove({ GuildID: guild.id})
  }

  const autoresponderdata = await autoresponderschema.findOne({ GuildID: guild.id })

  if (autoresponderdata) {
    await autoresponderschema.deleteMany({ GuildID: guild.id })
  }

  const embed = new MessageEmbed()

  .setColor(embedcolor)
  .setTitle('left guild')
  .setDescription(`name: **${guild.name}** | owner: <@${guild.ownerId}> | id: **${guild.id}** | membercount: **${guild.memberCount}**`)
  .setFooter({ text: `we're now at ${client.guilds.cache.size} servers` })

  logchannel.send({ embeds: [embed] })
})

//
client.on('messageCreate', async (message) => {

  if (!message.guild.me.permissions.has(['SEND_MESSAGES', 'EMBED_LINKS'])) return;

  afkschema.findOne({ GuildID: message.guild?.id, UserID: message.author?.id }, async(err, data) => {

    if(data) {

      const timepassed = Date.now() - data.TimeAgo

      let days = Math.floor(timepassed / 864000000);
      let hours = Math.floor(timepassed / 3600000) % 24;
      let minutes = Math.floor(timepassed / 60000) % 60
      let seconds = Math.floor(timepassed / 1000) % 60;

      let uptimedays = days
      if (uptimedays) {
        uptimedays = `${days} days, `;
      } else {
        uptimedays = ''
      }

      let uptimehours = hours
      if (uptimehours) {
        uptimehours = `${hours} hours, `;
      } else {
        uptimehours = ''
      }

      let uptimeminutes = minutes
      if (uptimeminutes) {
        uptimeminutes = `${minutes} minutes, `;
      } else {
        uptimeminutes = ''
      }

      let uptimeseconds = seconds
      if (uptimeseconds) {
        uptimeseconds = `${seconds} seconds`;
      } else {
        uptimeseconds = ''
      }

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setAuthor({ name: `${message.author.username + " is no longer afk.."}`, iconURL: `${message.author.displayAvatarURL({ size: 1024, dynamic: true })}` })
      .setDescription(`welcome back, you were gone for **${uptimedays}${uptimehours}${uptimeminutes}${uptimeseconds}**`)

      data.delete()
      
      return message.channel.send({ embeds: [embed] })

    } else return;
  })

  if(message.mentions.members?.first()) {

    afkschema.findOne({ GuildID: message.guild.id, UserID: message.mentions.members.first().id }, async(err, data) => {

      if(data) {

        const timepassed = Date.now() - data.TimeAgo

        let days = Math.floor(timepassed / 864000000);
        let hours = Math.floor(timepassed / 3600000) % 24;
        let minutes = Math.floor(timepassed / 60000) % 60
        let seconds = Math.floor(timepassed / 1000) % 60;

        let uptimedays = days
        if (uptimedays) {
          uptimedays = `${days} days, `;
        } else {
          uptimedays = ''
        }

        let uptimehours = hours
        if (uptimehours) {
        uptimehours = `${hours} hours, `;
        } else {
          uptimehours = ''
        }

        let uptimeminutes = minutes
        if (uptimeminutes) {
          uptimeminutes = `${minutes} minutes, `;
        } else {
          uptimeminutes = ''
        }

        let uptimeseconds = seconds
        if (uptimeseconds) {
          uptimeseconds = `${seconds} seconds`;
        } else {
          uptimeseconds = ''
        }

        const user = message.guild.members.cache.get(data.UserID)

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setAuthor({ name: `${user.user.username + " is currently afk.."}`, iconURL: `${user.user.displayAvatarURL({ size: 1024, dynamic: true })}` })
        .setDescription(`> ${data.Message} — ${uptimedays}${uptimehours}${uptimeminutes}${uptimeseconds}`)
        
        return message.channel.send({ embeds: [embed] })
      } else return;
    })
  }

  const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

  if (!globaldata) return;

  const blacklistedusers = globaldata.BlacklistedUsers

  if (!blacklistedusers.includes(message.author.id)) {

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    let guildprefix1;

    let mentionregex = message.content.match(new RegExp(`^<@!?(${client.user.id})>`, 'gi'));
    if (mentionregex) {
      guildprefix1 = `${mentionregex[0]} `
    } else {
      guildprefix1 = guildprefix
    }

    if (message.author.bot || message.channel.type === 'dm') return;

    autoresponderschema.find({ GuildID: message.guild.id }, async(err, data) => {

      if (!data) return;

      data.map((ar) => {
        if (message.content.includes(ar.Trigger)) {
          return message.channel.send({ content: ar.Response })
        }
      })
    })

    if (message.content.match(new RegExp(`^<@!?${client.user.id}>( |)$`))) return message.channel.send(`prefix: \`${guildprefix}\``).then((msg) => {
      setTimeout(() => msg.delete(), 3000);
    })

    if(!message.content.startsWith(guildprefix1)) return;
 
    const args = message.content.slice(guildprefix1.length).trim().split(/ +/g);
    const cmd = args.shift().toLowerCase();
    if(cmd.length == 0) return;
      
    let command = client.commands.get(cmd)
    if(!command) command = client.commands.get(client.aliases.get(cmd));
 
    if (!cooldowns.has(command?.name)) {
      cooldowns.set(command?.name, new Collection());
    }

    const now = Date.now();
    const timestamps = cooldowns.get(command?.name);
    const cooldownamount = (command?.cooldown || 3) * 1000;

    if (timestamps.has(message.author.id)) {

      const expirationtime = timestamps.get(message.author.id) + cooldownamount;
            
      if (now < expirationtime) {
  
        const timeleft = (expirationtime - now) / 1000;

        return message.channel.send(`wait **${timeleft.toFixed(1)}** second(s) to run a command again`).then((msg) => {
          setTimeout(() => msg.delete().catch(() => { return; }), 2000);
        })
      }
    }

    timestamps.set(message.author.id, now);
    setTimeout(() => timestamps.delete(message.author.id), cooldownamount)

    if(command) {
      
      command.run(client, message, args)

      const logchannel = client.channels.cache.get('1267078858021277787')

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setDescription(`${message.author} said **${message.content}** in ${message.guild.name}\`(${message.guild.id})\``)

      return logchannel.send({ embeds: [embed] })
    }

  } else {
    return message.channel.send(`you're blacklisted...`)
  }
})

//
client.on('messageDelete', async (message) => {

  if (message.author) {
    client.snipes.set(message.channel.id, {
      content: message.content,
      author: message.author.tag,
      image: message.attachments.first() ? message.attachments.first().proxyURL : null
    })
  }
})

//
client.on('messageUpdate', async (oldmessage, newMessage) => {

  if (oldmessage.author) {
    client.editsnipes.set(oldmessage.channel.id, {
      content: newMessage.content,
      author: newMessage.author.tag,
      image: newMessage.attachments.first() ? newMessage.attachments.first().proxyURL : null
    })
  }
})

//
client.on('presenceUpdate', async (oldMember, newMember) => {

  if (newMember?.status === "invisible" || newMember?.status === "offline" || oldMember?.status === "invisible" || oldMember?.status === "offline") return;

  const globaldata = await globaldataschema.findOne({ GuildID: newMember.guild.id });

  if (!globaldata) return;

  const array = globaldata.VanityRoles

  if (array < 0) return;

  if(newMember.activities[0]?.type === 'CUSTOM' && newMember.activities[0]?.state?.includes(`.gg/${globaldata.Vanity}`) || newMember.activities[0]?.state?.includes(`/${globaldata.Vanity}`)) {

    if (!newMember.member.roles?.cache.hasAny(...array)) {

      newMember.member?.roles.add(array, 'added vanity role(s)').then(() => {

        if (globaldata.VanityMessage) {
    
          let vanitymessage = globaldata.VanityMessage

          vanitymessage = vanitymessage.replace('{user.mention}', `<@${newMember.member.id}>`);
          vanitymessage = vanitymessage.replace('{user.name}', newMember.member.user.username);
          vanitymessage = vanitymessage.replace('{user.tag}', newMember.member.user.tag);
          vanitymessage = vanitymessage.replace('{user.id}', newMember.member.id);
          vanitymessage = vanitymessage.replace('{server.name}', newMember.guild.name);

          var vanitymsg = vanitymessage

        } else {

          const vanitymsg1 = `<@${newMember.member.id}> has vanity in their status`
      
          vanitymsg = vanitymsg1
        }

        if (globaldata.VanityLogChannel) {
        
          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${vanitymsg}`)

          const channel = newMember.guild.channels.cache.get(globaldata.VanityLogChannel)

          if (!channel) return;

          channel.send({ embeds: [embed] })
        }

      }).catch(() => { return; })
    }

  } else {

    if (newMember.member?.roles.cache.hasAny(...array)) {

      newMember.member.roles.remove(array, 'removed vanity role(s)').then(() => {

        if (globaldata.VanityLogChannel) {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`<@${newMember.member.id}> no longer has vanity in their status`)

          const channel = newMember.guild.channels.cache.get(globaldata.VanityLogChannel)

          if (!channel) return;

          channel.send({ embeds: [embed] })
        }
          
      }).catch(() => { return; })
    }
  }
})

//
client.on('guildMemberAdd', async (member) => {

  autoroleschema.findOne({ GuildID: member.guild.id }, async(err, data) => {
        
    if (!data) return;

    const autorole = member.guild.roles.cache.get(data.RoleID)

    if (!autorole) return;

    member.roles.add(autorole.id).catch(() => { return; })
  })

  globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

    // WELCOME

    const welcomemessage = data.WelcomeMessage

    if (!welcomemessage) return;

    const welcomechannel = data.WelcomeChannel

    if (!welcomechannel) return;

    const channel = member.guild.channels.cache.get(welcomechannel)

    if (!channel) return;

    let welcome = welcomemessage

    welcome = welcome.replace('{user.mention}', member);
    welcome = welcome.replace('{user.name}', member.user.username);
    welcome = welcome.replace('{user.tag}', member.user.tag);
    welcome = welcome.replace('{user.id}', member.user.id);
    welcome = welcome.replace('{server.membercount}', member.guild.memberCount);
    const ordinal = (member.guild.memberCount.toString().endsWith(1) && !member.guild.memberCount.toString().endsWith(11)) ? 'st' : (member.guild.memberCount.toString().endsWith(2) && !member.guild.memberCount.toString().endsWith(12)) ? 'nd' : (member.guild.memberCount.toString().endsWith(3) && !member.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
    welcome = welcome.replace('{server.humanmembercount}', member.guild.memberCount + ordinal);
    welcome = welcome.replace('{server.name}', member.guild.name);

    new EmbedBuilder(channel, welcome)
  })

  if (!member.guild.me.permissions.has(['VIEW_AUDIT_LOG'])) return;

  const globaldata = await globaldataschema.findOne({ GuildID: member.guild.id })

  if (globaldata.AntiNukeToggle === 'true') {

    const auditlogs = await member.guild.fetchAuditLogs({ limit: 1, type: 'BOT_ADD' }).catch(() => { return; })

    if (!auditlogs) return;

    const botlog = auditlogs?.entries.first();

    if (botlog) {

      const { executor, target, createdTimestamp } = botlog;

      const owner = await member.guild.fetchOwner();

      if (executor.id == owner.id || executor.id == client.user.id) return;
      if (!target.bot) return;
      if (target.id !== member.id) return;

      const whitelistedusers = globaldata.AntiNukeWhitelistedUsers
      if(!whitelistedusers) return;
      if (whitelistedusers.includes(executor.id)) return;

      const whitelistedroles = globaldata.AntiNukeWhitelistedRoles
      if(!whitelistedroles) return;
      const nuker = member.guild.members.cache.get(executor.id);
      if (nuker?.roles.cache.hasAny(...whitelistedroles)) return;

      const timestamp = Date.now();
      const logtime = createdTimestamp.toString();
      const eventtime = timestamp.toString();
      const log = logtime.slice(0, 3);
      const event = eventtime.slice(0, 3);

      if (log === event) {

        await member.guild.members.ban(executor.id, { reason: 'unauthorized user added a bot' }).then(() => {

          globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

            if (data.AntiNukeChannel) {

              const embed = new MessageEmbed()

              .setColor(embedcolor)
              .setDescription(`<@${executor.id}> added a bot but was immediately banned`)

              var antilogchannel = member.guild.channels.cache.get(data.AntiNukeChannel)
              if (!antilogchannel) return;

              antilogchannel.send({ embeds: [embed] })
            
            } else {
              return;
            }
          })
        
        }).catch(() => { return; })

        await member.guild.members.ban(target.id, { reason: 'bot added by unauthorized user' }).catch(() => { return; })
      }
    }

  } else {
    return;
  }
})

//
client.on('guildMemberRemove', async (member) => {

  if (member.id === client.user.id) return;

  globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

    // GOODBYE

    let goodbyemessage;

    if (!data.GoodbyeMesage) return;

    if (data.GoodbyeMessage) {
      goodbyemessage = data.GoodbyeMessage
    }

    let goodbyechannel;

    if (!data.GoodbyeChannel) return;

    if (data.GoodbyeChannel) {
      goodbyechannel = data.GoodbyeChannel
    }

    const channel = member.guild.channels.cache.get(goodbyechannel)

    if (!channel) return;

    let goodbye = goodbyemessage

    goodbye = goodbye.replace('{user.mention}', member);
    goodbye = goodbye.replace('{user.name}', member.user.username);
    goodbye = goodbye.replace('{user.tag}', member.user.tag);
    goodbye = goodbye.replace('{user.id}', member.user.id);
    goodbye = goodbye.replace('{server.membercount}', member.guild.memberCount);
    const ordinal1 = (member.guild.memberCount.toString().endsWith(1) && !member.guild.memberCount.toString().endsWith(11)) ? 'st' : (member.guild.memberCount.toString().endsWith(2) && !member.guild.memberCount.toString().endsWith(12)) ? 'nd' : (member.guild.memberCount.toString().endsWith(3) && !member.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
    goodbye = goodbye.replace('{server.humanmembercount}', member.guild.memberCount + ordinal1);
    goodbye = goodbye.replace('{server.name}', member.guild.name);

    new EmbedBuilder(channel, goodbye)
  })
})

//
client.on('guildBanAdd', async (member) => {

  if (!member.guild.me.permissions.has(['VIEW_AUDIT_LOG'])) return;

  const globaldata = await globaldataschema.findOne({ GuildID: member.guild.id })

  if (globaldata.AntiNukeToggle === 'true') {

    const auditlogs = await member.guild.fetchAuditLogs({ limit: 1, type: 'MEMBER_BAN_ADD' }).catch(() => { return; })

    if (!auditlogs) return;

    const banlog = auditlogs?.entries.first();

    if (!banlog) return;

    const { executor, createdTimestamp } = banlog;

    const owner = await member.guild.fetchOwner();

    if (executor.id == owner.id || executor.id == client.user.id) return;

    const whitelistedusers = globaldata.AntiNukeWhitelistedUsers
    if(!whitelistedusers) return;
    if (whitelistedusers.includes(executor.id)) return;

    const whitelistedroles = globaldata.AntiNukeWhitelistedRoles
    if(!whitelistedroles) return;
    const nuker = member.guild.members.cache.get(executor.id);
    if (nuker?.roles.cache.hasAny(...whitelistedroles)) return;

    const timestamp = Date.now();
    const logtime = createdTimestamp.toString();
    const eventtime = timestamp.toString();
    const log = logtime.slice(0, 3);
    const event = eventtime.slice(0, 3);

    if (log === event) {

      await member.guild.members.ban(executor.id, { reason: 'unauthorized user banned a member' }).then(() => {

        globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

          if (data.AntiNukeChannel) {

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setDescription(`<@${executor.id}> banned a member but was immediately banned`)

            var antilogchannel = member.guild.channels.cache.get(data.AntiNukeChannel)
            if (!antilogchannel) return;

            antilogchannel.send({ embeds: [embed] })
            
          } else {
            return;
          }
        })
        
      }).catch(() => { return; })
    }
    
  } else {
    return;    
  }
})

//
client.on('guildMemberRemove', async (member) => {

  if (member.id === client.user.id) return;

  if (!member.guild.me.permissions.has(['VIEW_AUDIT_LOG'])) return;

  const globaldata = await globaldataschema.findOne({ GuildID: member.guild.id })

  if (globaldata.AntiNukeToggle === 'true') {

    const auditlogs = await member.guild.fetchAuditLogs({ limit: 1, type: 'MEMBER_KICK' }).catch(() => { return; })

    if (!auditlogs) return;

    const kicklog = auditlogs?.entries.first();

    if (!kicklog) return;

    const { executor, target, createdTimestamp } = kicklog;

    const owner = await member.guild.fetchOwner();

    if (executor.id == owner.id || executor.id == client.user.id) return;
    if (member.id !== target.id) return;

    const whitelistedusers = globaldata.AntiNukeWhitelistedUsers
    if(!whitelistedusers) return;
    if (whitelistedusers.includes(executor.id)) return;

    const whitelistedroles = globaldata.AntiNukeWhitelistedRoles
    if(!whitelistedroles) return;
    const nuker = member.guild.members.cache.get(executor.id);
    if (nuker?.roles.cache.hasAny(...whitelistedroles)) return;

    const timestamp = Date.now();
    const logtime = createdTimestamp.toString();
    const eventtime = timestamp.toString();
    const log = logtime.slice(0, 3);
    const event = eventtime.slice(0, 3);

    if (log === event) {

      await member.guild.members.ban(executor.id, { reason: 'unauthorized user kicked a member' }).then(() => {

        globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

          if (data.AntiNukeChannel) {

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setDescription(`<@${executor.id}> kicked a member but was immediately banned`)

            var antilogchannel = member.guild.channels.cache.get(data.AntiNukeChannel)
            if (!antilogchannel) return;

            antilogchannel.send({ embeds: [embed] })
            
          } else {
            return;
          }
        })
        
      }).catch(() => { return; })
    }
    
  } else {
    return;    
  }
})

//
client.on('channelCreate', async (channel) => {

  if (!channel.guild.me.permissions.has(['VIEW_AUDIT_LOG'])) return;

  const globaldata = await globaldataschema.findOne({ GuildID: channel.guild.id })

  if (globaldata.AntiNukeToggle === 'true') {

    const auditlogs = await channel.guild.fetchAuditLogs({ limit: 1, type: 'CHANNEL_CREATE' }).catch(() => { return; })

    if (!auditlogs) return;

    const channellog = auditlogs?.entries.first();

    if (!channellog) return;

    const { executor, createdTimestamp } = channellog;

    const owner = await channel.guild.fetchOwner();

    if (executor.id == owner.id || executor.id == client.user.id) return;

    const whitelistedusers = globaldata.AntiNukeWhitelistedUsers
    if(!whitelistedusers) return;
    if (whitelistedusers.includes(executor.id)) return;

    const whitelistedroles = globaldata.AntiNukeWhitelistedRoles
    if(!whitelistedroles) return;
    const nuker = channel.guild.members.cache.get(executor.id);
    if (nuker?.roles.cache.hasAny(...whitelistedroles)) return;

    const timestamp = Date.now();
    const logtime = createdTimestamp.toString();
    const eventtime = timestamp.toString();
    const log = logtime.slice(0, 3);
    const event = eventtime.slice(0, 3);

    if (log === event) {

      await channel.guild.members.ban(executor.id, { reason: 'unauthorized user created a channel' }).then(() => {

        globaldataschema.findOne({ GuildID: channel.guild.id }, async function(err, data) {

          if (data.AntiNukeChannel) {

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setDescription(`<@${executor.id}> created a channel but was immediately banned`)

            var antilogchannel = channel.guild.channels.cache.get(data.AntiNukeChannel)
            if (!antilogchannel) return;

            antilogchannel.send({ embeds: [embed] })
            
          } else {
            return;
          }
        })
        
      }).catch(() => { return; })

      channel.delete({ reason: 'channel created by unauthorized user' }).catch(() => { return; })
    }
    
  } else {
    return;    
  }
})

//
client.on('channelDelete', async (channel) => {

  if (!channel.guild.me.permissions.has(['VIEW_AUDIT_LOG'])) return;

  const globaldata = await globaldataschema.findOne({ GuildID: channel.guild.id })

  if (globaldata.AntiNukeToggle === 'true') {

    const auditlogs = await channel.guild.fetchAuditLogs({ limit: 1, type: 'CHANNEL_DELETE' }).catch(() => { return; })

    if (!auditlogs) return;

    const channellog = auditlogs?.entries.first();

    if (!channellog) return;

    const { executor, createdTimestamp } = channellog;

    const owner = await channel.guild.fetchOwner();

    if (executor.id == owner.id || executor.id == client.user.id) return;

    const whitelistedusers = globaldata.AntiNukeWhitelistedUsers
    if(!whitelistedusers) return;
    if (whitelistedusers.includes(executor.id)) return;

    const whitelistedroles = globaldata.AntiNukeWhitelistedRoles
    if(!whitelistedroles) return;
    const nuker = channel.guild.members.cache.get(executor.id);
    if (nuker?.roles.cache.hasAny(...whitelistedroles)) return;

    const timestamp = Date.now();
    const logtime = createdTimestamp.toString();
    const eventtime = timestamp.toString();
    const log = logtime.slice(0, 3);
    const event = eventtime.slice(0, 3);

    if (log === event) {

      await channel.guild.members.ban(executor.id, { reason: 'unauthorized user deleted a channel' }).then(() => {

        globaldataschema.findOne({ GuildID: channel.guild.id }, async function(err, data) {

          if (data.AntiNukeChannel) {

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setDescription(`<@${executor.id}> deleted a channel but was immediately banned`)

            var antilogchannel = channel.guild.channels.cache.get(data.AntiNukeChannel)
            if (!antilogchannel) return;

            antilogchannel.send({ embeds: [embed] })
            
          } else {
            return;
          }
        })
        
      }).catch(() => { return; })
    }
    
  } else {
    return;    
  }
})

//
client.on('roleCreate', async (role) => {

  if (!role.guild.me.permissions.has(['VIEW_AUDIT_LOG'])) return;

  const globaldata = await globaldataschema.findOne({ GuildID: role.guild.id })

  if (globaldata.AntiNukeToggle === 'true') {

    const auditlogs = await role.guild.fetchAuditLogs({ limit: 1, type: 'ROLE_CREATE' }).catch(() => { return; })

    if (!auditlogs) return;

    const rolelog = auditlogs?.entries.first();

    if (!rolelog) return;

    const { executor, createdTimestamp } = rolelog;

    const owner = await role.guild.fetchOwner();

    if (executor.id == owner.id || executor.id == client.user.id) return;
    if (role.managed) return;

    const whitelistedusers = globaldata.AntiNukeWhitelistedUsers
    if(!whitelistedusers) return;
    if (whitelistedusers.includes(executor.id)) return;

    const whitelistedroles = globaldata.AntiNukeWhitelistedRoles
    if(!whitelistedroles) return;
    const nuker = role.guild.members.cache.get(executor.id);
    if (nuker?.roles.cache.hasAny(...whitelistedroles)) return;

    const timestamp = Date.now();
    const logtime = createdTimestamp.toString();
    const eventtime = timestamp.toString();
    const log = logtime.slice(0, 3);
    const event = eventtime.slice(0, 3);

    if (log === event) {

      await role.guild.members.ban(executor.id, { reason: 'unauthorized user created a role' }).then(() => {

        globaldataschema.findOne({ GuildID: role.guild.id }, async function(err, data) {

          if (data.AntiNukeChannel) {

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setDescription(`<@${executor.id}> created a role but was immediately banned`)

            var antilogchannel = role.guild.channels.cache.get(data.AntiNukeChannel)
            if (!antilogchannel) return;

            antilogchannel.send({ embeds: [embed] })
            
          } else {
            return;
          }
        })
        
      }).catch(() => { return; })

      role.delete({ reason: 'role created by unauthorized user' }).catch(() => { return; })
    }
    
  } else {
    return;    
  }
})

//
client.on('roleDelete', async (role) => {

  if (!role.guild.me.permissions.has(['VIEW_AUDIT_LOG'])) return;

  const globaldata = await globaldataschema.findOne({ GuildID: role.guild.id })

  if (globaldata.AntiNukeToggle === 'true') {

    const auditlogs = await role.guild.fetchAuditLogs({ limit: 1, type: 'ROLE_DELETE' }).catch(() => { return; })

    if (!auditlogs) return;

    const rolelog = auditlogs?.entries.first();

    if (!rolelog) return;

    const { executor, createdTimestamp } = rolelog;

    const owner = await role.guild.fetchOwner();

    if (executor.id == owner.id || executor.id == client.user.id) return;
    if (role.managed) return;

    const whitelistedusers = globaldata.AntiNukeWhitelistedUsers
    if(!whitelistedusers) return;
    if (whitelistedusers.includes(executor.id)) return;

    const whitelistedroles = globaldata.AntiNukeWhitelistedRoles
    if(!whitelistedroles) return;
    const nuker = role.guild.members.cache.get(executor.id);
    if (nuker?.roles.cache.hasAny(...whitelistedroles)) return;

    const timestamp = Date.now();
    const logtime = createdTimestamp.toString();
    const eventtime = timestamp.toString();
    const log = logtime.slice(0, 3);
    const event = eventtime.slice(0, 3);

    if (log === event) {

      await role.guild.members.ban(executor.id, { reason: 'unauthorized user deleted a role' }).then(() => {

        globaldataschema.findOne({ GuildID: role.guild.id }, async function(err, data) {

          if (data.AntiNukeChannel) {

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setDescription(`<@${executor.id}> deleted a role but was immediately banned`)

            var antilogchannel = role.guild.channels.cache.get(data.AntiNukeChannel)
            if (!antilogchannel) return;

            antilogchannel.send({ embeds: [embed] })
            
          } else {
            return;
          }
        })
        
      }).catch(() => { return; })
    }
    
  } else {
    return;    
  }
})

//
client.on('roleUpdate', async (role, newRole) => {

  if (!role.guild.me.permissions.has(['VIEW_AUDIT_LOG'])) return;

  const globaldata = await globaldataschema.findOne({ GuildID: role.guild.id })

  if (globaldata.AntiNukeToggle === 'true') {

    const auditlogs = await role.guild.fetchAuditLogs({ limit: 1, type: 'ROLE_UPDATE' }).catch(() => { return; })

    if (!auditlogs) return;

    const rolelog = auditlogs?.entries.first();

    if (!rolelog) return;

    const { executor, createdTimestamp } = rolelog;

    const owner = await role.guild.fetchOwner();

    if (executor.id == owner.id || executor.id == client.user.id) return;
    if (role.managed) return;

    const whitelistedusers = globaldata.AntiNukeWhitelistedUsers
    if(!whitelistedusers) return;
    if (whitelistedusers.includes(executor.id)) return;

    const whitelistedroles = globaldata.AntiNukeWhitelistedRoles
    if(!whitelistedroles) return;
    const nuker = role.guild.members.cache.get(executor.id);
    if (nuker?.roles.cache.hasAny(...whitelistedroles)) return;

    const timestamp = Date.now();
    const logtime = createdTimestamp.toString();
    const eventtime = timestamp.toString();
    const log = logtime.slice(0, 3);
    const event = eventtime.slice(0, 3);

    if (log === event) {

      await role.guild.members.ban(executor.id, { reason: 'unauthorized user updated a role' }).then(() => {

        globaldataschema.findOne({ GuildID: role.guild.id }, async function(err, data) {

          if (data.AntiNukeChannel) {

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setDescription(`<@${executor.id}> updated a role but was immediately banned`)

            var antilogchannel = role.guild.channels.cache.get(data.AntiNukeChannel)
            if (!antilogchannel) return;

            antilogchannel.send({ embeds: [embed] })
            
          } else {
            return;
          }
        })

        newRole.setPermissions(role.permissions, 'role has been reverted, unauthorized user updated it').catch(() => { return; })
        
      }).catch(() => { return; })
    }
    
  } else {
    return;    
  }
})

//
client.on('guildMemberUpdate', async (member, newMember) => {

  if (!member.guild.me.permissions.has(['VIEW_AUDIT_LOG'])) return;

  const globaldata = await globaldataschema.findOne({ GuildID: member.guild.id })

  if (globaldata.AntiNukeToggle === 'true') {

    const auditlogs = await member.guild.fetchAuditLogs({ limit: 1, type: 'MEMBER_ROLE_UPDATE' }).catch(() => { return; })

    if (!auditlogs) return;

    const memberlog = auditlogs?.entries.first();

    if (!memberlog) return;

    const { executor, target, createdTimestamp } = memberlog;

    const owner = await member.guild.fetchOwner();

    if (executor.id == owner.id || executor.id == client.user.id) return;
    if (newMember.user.id !== target.id) return;

    const whitelistedusers = globaldata.AntiNukeWhitelistedUsers
    if(!whitelistedusers) return;
    if (whitelistedusers.includes(executor.id)) return;

    const whitelistedroles = globaldata.AntiNukeWhitelistedRoles
    if(!whitelistedroles) return;
    const nuker = member.guild.members.cache.get(executor.id);
    if (nuker?.roles.cache.hasAny(...whitelistedroles)) return;

    const timestamp = Date.now();
    const logtime = createdTimestamp.toString();
    const eventtime = timestamp.toString();
    const log = logtime.slice(0, 3);
    const event = eventtime.slice(0, 3);

    if (log === event) {

      if (!member.permissions.has(Permissions.FLAGS.ADMINISTRATOR) && newMember.permissions.has(Permissions.FLAGS.ADMINISTRATOR)) {

        await member.guild.members.ban(executor.id, { reason: 'unauthorized user updated a member permission' }).then(() => {

          globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

            if (data.AntiNukeChannel) {

              const embed = new MessageEmbed()

              .setColor(embedcolor)
              .setDescription(`<@${executor.id}> updated a member permissions but was immediately banned`)

              var antilogchannel = member.guild.channels.cache.get(data.AntiNukeChannel)
              if (!antilogchannel) return;

              antilogchannel.send({ embeds: [embed] })
            
            } else {
              return;
            }
          })
        
        }).catch(() => { return; })

        await member.guild.members.ban(target.id, { reason: 'permissions updated by unauthorized user' }).catch(() => { return; })

      } else if (!member.permissions.has(Permissions.FLAGS.BAN_MEMBERS) && newMember.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) {

        await member.guild.members.ban(executor.id, { reason: 'unauthorized user updated a member permission' }).then(() => {

          globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

            if (data.AntiNukeChannel) {

              const embed = new MessageEmbed()

              .setColor(embedcolor)
              .setDescription(`<@${executor.id}> updated a member permissions but was immediately banned`)

              var antilogchannel = member.guild.channels.cache.get(data.AntiNukeChannel)
              if (!antilogchannel) return;

              antilogchannel.send({ embeds: [embed] })
            
            } else {
              return;
            }
          })
        
        }).catch(() => { return; })

        await member.guild.members.ban(target.id, { reason: 'permissions updated by unauthorized user' }).catch(() => { return; })

      } else if (!member.permissions.has(Permissions.FLAGS.KICK_MEMBERS) && newMember.permissions.has(Permissions.FLAGS.KICK_MEMBERS)) {

        await member.guild.members.ban(executor.id, { reason: 'unauthorized user updated a member permission' }).then(() => {

          globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

            if (data.AntiNukeChannel) {

              const embed = new MessageEmbed()

              .setColor(embedcolor)
              .setDescription(`<@${executor.id}> updated a member permissions but was immediately banned`)

              var antilogchannel = member.guild.channels.cache.get(data.AntiNukeChannel)
              if (!antilogchannel) return;

              antilogchannel.send({ embeds: [embed] })
            
            } else {
              return;
            }
          })
        
        }).catch(() => { return; })

        await member.guild.members.ban(target.id, { reason: 'permissions updated by unauthorized user' }).catch(() => { return; })

      } else if (!member.permissions.has(Permissions.FLAGS.MANAGE_WEBHOOKS) && newMember.permissions.has(Permissions.FLAGS.MANAGE_WEBHOOKS)) {

        await member.guild.members.ban(executor.id, { reason: 'unauthorized user updated a member permission' }).then(() => {

          globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

            if (data.AntiNukeChannel) {

              const embed = new MessageEmbed()

              .setColor(embedcolor)
              .setDescription(`<@${executor.id}> updated a member permissions but was immediately banned`)

              var antilogchannel = member.guild.channels.cache.get(data.AntiNukeChannel)
              if (!antilogchannel) return;

              antilogchannel.send({ embeds: [embed] })
            
            } else {
              return;
            }
          })
        
        }).catch(() => { return; })

        await member.guild.members.ban(target.id, { reason: 'permissions updated by unauthorized user' }).catch(() => { return; })

      } else if (!member.permissions.has(Permissions.FLAGS.MANAGE_GUILD) && newMember.permissions.has(Permissions.FLAGS.MANAGE_GUILD)) {

        await member.guild.members.ban(executor.id, { reason: 'unauthorized user updated a member permission' }).then(() => {

          globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

            if (data.AntiNukeChannel) {

              const embed = new MessageEmbed()

              .setColor(embedcolor)
              .setDescription(`<@${executor.id}> updated a member permissions but was immediately banned`)

              var antilogchannel = member.guild.channels.cache.get(data.AntiNukeChannel)
              if (!antilogchannel) return;

              antilogchannel.send({ embeds: [embed] })
            
            } else {
              return;
            }
          })
        
        }).catch(() => { return; })

        await member.guild.members.ban(target.id, { reason: 'permissions updated by unauthorized user' }).catch(() => { return; })

      } else if (!member.permissions.has(Permissions.FLAGS.MANAGE_ROLES) && newMember.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) {

        await member.guild.members.ban(executor.id, { reason: 'unauthorized user updated a member permission' }).then(() => {

          globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

            if (data.AntiNukeChannel) {

              const embed = new MessageEmbed()

              .setColor(embedcolor)
              .setDescription(`<@${executor.id}> updated a member permissions but was immediately banned`)

              var antilogchannel = member.guild.channels.cache.get(data.AntiNukeChannel)
              if (!antilogchannel) return;

              antilogchannel.send({ embeds: [embed] })
            
            } else {
              return;
            }
          })
        
        }).catch(() => { return; })

        await member.guild.members.ban(target.id, { reason: 'permissions updated by unauthorized user' }).catch(() => { return; })

      } else if (!member.permissions.has(Permissions.FLAGS.MANAGE_CHANNELS) && newMember.permissions.has(Permissions.FLAGS.MANAGE_CHANNELS)) {

        await member.guild.members.ban(executor.id, { reason: 'unauthorized user updated a member permission' }).then(() => {

          globaldataschema.findOne({ GuildID: member.guild.id }, async function(err, data) {

            if (data.AntiNukeChannel) {

              const embed = new MessageEmbed()

              .setColor(embedcolor)
              .setDescription(`<@${executor.id}> updated a member permissions but was immediately banned`)

              var antilogchannel = member.guild.channels.cache.get(data.AntiNukeChannel)
              if (!antilogchannel) return;

              antilogchannel.send({ embeds: [embed] })
            
            } else {
              return;
            }
          })
        
        }).catch(() => { return; })

        await member.guild.members.ban(target.id, { reason: 'permissions updated by unauthorized user' }).catch(() => { return; })
      }
    }
    
  } else {
    return;    
  }
})

//
process.on('unhandledRejection', (error, promise) => {

  const channel = client.channels.cache.get('1296036562093740104')

  const embed = new MessageEmbed()
      
  .setColor(embedcolor)
  .setAuthor({ name: `${client.user.username}`, iconURL: `${client.user.displayAvatarURL({ dynamic: true })}` })
  .setTitle(`Anti-Crash: Unhandled Rejection`)
  .addField('**Error**', `\`\`\`${error.stack}\`\`\``, false)
  .addField('**Promise**', `\`\`\`${promise}\`\`\``, false)
  .setTimestamp()

  return channel?.send({ embeds: [embed] })
});

//
process.on('uncaughtException', (err, origin) => {

  const channel = client.channels.cache.get('1296036562093740104')

  const embed = new MessageEmbed()

  .setColor(embedcolor)
  .setAuthor({ name: `${client.user.username}`, iconURL: `${client.user.displayAvatarURL({ dynamic: true })}` })
  .setTitle(`Anti-Crash: Uncaught Exception`)
  .addField('**Origin**', `\`\`\`${origin}\`\`\``, false)
  .addField('**Error**', `\`\`\`${err.stack}\`\`\``, false)
  .setTimestamp()

  channel?.send({ embeds: [embed] })
});

//
process.on('uncaughtExceptionMonitor', (err, origin) => {

  const channel = client.channels.cache.get('1296036562093740104')

  const embed = new MessageEmbed()
  
  .setColor(embedcolor)
  .setAuthor({ name: `crash`, iconURL: `${client.user.displayAvatarURL({ dynamic: true })}` })
  .setTitle(`Anti-Crash: Uncaught Exception Monitor`)
  .addField('**Origin**', `\`\`\`${origin}\`\`\``, false)
  .addField('**Error**', `\`\`\`${err.stack}\`\`\``, false)
  .setTimestamp()

  channel?.send({ embeds: [embed] })
});

//
process.on('multipleResolves', (type, promise, reason) => {

  const channel = client.channels.cache.get('1296036562093740104')

  const embed = new MessageEmbed()
  
  .setColor(embedcolor)
  .setAuthor({ name: `${client.user.username}`, iconURL: `${client.user.displayAvatarURL({ dynamic: true })}` })
  .setTitle(`Anti-Crash: Multiple Resolves`)
  .addField('**Type**', `\`\`\`${type}\`\`\``, false)
  .addField('**Promise**', `\`\`\`${promise}\`\`\``, false)
  .addField('**Reason**', `\`\`\`${reason.stack}\`\`\``, false)
  .setTimestamp()

  return channel?.send({ embeds: [embed] })
})

client.login(token)