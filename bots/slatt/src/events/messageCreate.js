const db = require('quick.db')
const {
  MessageEmbed
} = require('discord.js')
const humanizeDuration = require('humanize-duration');
const cooldowns = new Map()

module.exports = async (client, message) => {
  if (db.get(`BLACKLIST_${message.author.id}`)) return
  const { stripIndent } = require('common-tags');
  if (message.channel.type === 'dm' || !message.channel.viewable || message.author.bot) return
  const prefixCheck = await client.db.custom_prefix.findOne({ where: { userID: message.author.id } })
  let prefix
  if (prefixCheck && message.author.id === prefixCheck.userID && message.content.startsWith(message.author.username)) {
    prefix = message.author.username
  } else {
    const dbprefix = await client.db.prefix.findOne({ where: { guildID: message.guild.id } })
    if (dbprefix) {
      prefix = dbprefix.prefix
    } else {
      prefix = ';'
    }
  }
  message.prefix = prefix
  if (
    (message.content === `<@${client.user.id}>` || message.content === `<@!${client.user.id}>`) &&
    message.channel.permissionsFor(message.guild.me).has(['SEND_MESSAGES', 'EMBED_LINKS'])
  ) {
    const embed = new MessageEmbed()
      .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
      .setColor('#303135')
      .setTitle(`${client.user.username}`)
      .setDescription(`help [command/type]`)
      .setThumbnail(client.user.avatarURL())
      .addField(`Commands`, `${client.commands.size+client.subcommands.size}`, true)
      .addField(`Prefix`, message.prefix, true)
      .addField(`Invite`, `[Invite](https://discord.com/api/oauth2/authorize?client_id=${client.user.id}&permissions=8&scope=bot)`, true)
    message.reply({ embeds: [embed] })
  }
  const prefixRegex = new RegExp(`^(<@!?${client.user.id}>|slatt|SLATT|Slatt|${prefix.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})\\s*`);
  if (prefixRegex.test(message.content)) {
    const [, match] = message.content.match(prefixRegex);
    const args = message.content.slice(match.length).trim().split(/ +/g);
    const cmd = args.shift().toLowerCase();
    let command = client.commands.get(cmd) || client.aliases.get(cmd)
    if (command && message.author.id !== '288402111916539914' && message.author.id !== '540071388069756931') {
      setTimeout(() => cooldowns.delete(message.author.id), 3000);
      const cooldown = cooldowns.get(message.author.id);
      if (cooldown) {
        const remaining = humanizeDuration(cooldown - Date.now());
        const embed = new MessageEmbed()
          .setDescription(`> <:info:828536926603837441> ${message.author} You are on command cooldown for **${remaining}**`)
          .setColor("#78c6fe");
        return message.channel.send({ embeds: [embed] });
      }
    }
    if (command) {
      let subcommand = client.subcommands.get(command.name + ' ' + args[0]) || client.subcommand_aliases.get(command.name + ' ' + args[0])
      if (subcommand) {
        cooldowns.set(message.author.id, Date.now() + 3000);
        const permission = command.checkPermissions(message);
        if (!permission) return
        const toggled = await client.db.toggled_commands.findOne({ where: { guildID: message.guild.id, cmd: subcommand.base + ' ' + subcommand.name } })
        const whitelisted = await client.db.command_whitelists.findOne({ where: { guildID: message.guild.id, cmd: `${subcommand.base} ${subcommand.name}`, userID: message.member.id } })
        if (toggled && !whitelisted && !message.member.permissions.has('ADMINISTRATOR')) {
          const embed = new MessageEmbed()
            .setDescription(`<:redx:827632831999246346> ${message.author} \`Disabled\` subcommand: **${subcommand.base} ${subcommand.name}** is disabled in this server`)
            .setColor("#990000");
          message.channel.send({ embeds: [embed] })
          return
        }
        subcommand.run(message, args.slice(1)).catch(e => {
          client.logger.error(e)
          db.set(`TraceBack`, { error: e.stack, content: message.content, command: command.name + ' ' + subcommand.name, author: message.author, guild: message.guild })
          const embed = new MessageEmbed()
            .setDescription(`<:redx:827632831999246346> ${message.author} \`Command Error:\` There was an error executing the command **${command.name + ' ' + subcommand.name}**`)
            .setColor("#990000");
          message.channel.send({ embeds: [embed] })

        })
        const channel = client.channels.cache.get('866423825235312640')
        const  cmdlog = new MessageEmbed()
        .setAuthor(message.author.tag + ' ' + message.author.id, message.author.avatarURL({ dynamic: true }))
        .setDescription(stripIndent`Command: **${command.name} ${subcommand.name}**
        Channel: **${message.channel.name}** (${message.channel.id})
        Guild: **${message.guild.name}** (${message.guild.id})
        Admin: **${message.member.permissions.has(['MANAGE_MESSAGES', 'MANAGE_GUILD', 'MANAGE_CHANNELS', 'ADMINISTRATOR'])}**
        \`\`\`${message.content}\`\`\`
        `)
        .setColor('#303135')
        .setThumbnail(message.guild.iconURL({ dynamic: true }))
        if (channel) channel.send({embeds: [cmdlog]})
        return
      }
      const permission = command.checkPermissions(message);
      if (permission) {
        cooldowns.set(message.author.id, Date.now() + 3000);
        message.command = true;
        const toggled = await client.db.toggled_commands.findOne({ where: { guildID: message.guild.id, cmd: command.name } })
        const whitelisted = await client.db.command_whitelists.findOne({ where: { guildID: message.guild.id, cmd: `${command.name}`, userID: message.member.id } })
        if (toggled && !whitelisted && !message.member.permissions.has('ADMINISTRATOR')) {
          const embed = new MessageEmbed()
            .setDescription(`<:redx:827632831999246346> ${message.author} \`Disabled\` command: **${command.name}** is disabled in this server`)
            .setColor("#990000");
          message.channel.send({ embeds: [embed] })
          return
        }
        command.run(message, args).catch(e => {
          client.logger.error(e)
          db.set(`TraceBack`, {
            error: e.stack,
            content: message.content,
            command: command.name,
            author: message.author,
            guild: message.guild
          })
          const embed = new MessageEmbed()
            .setDescription(`<:redx:827632831999246346> ${message.author} \`Command Error:\` There was an error executing the command **${command.name}**`)
            .setColor("#990000");
          message.channel.send({ embeds: [embed] })
        })
        const channel = client.channels.cache.get('866423825235312640')
        const cmdlog = new MessageEmbed()
        .setAuthor(message.author.tag + ' ' + message.author.id, message.author.avatarURL({ dynamic: true }))
        .setDescription(stripIndent`
        Command: **${command.name}**
        Channel: **${message.channel.name}** (${message.channel.id})
        Guild: **${message.guild.name}** (${message.guild.id})
        Admin: **${message.member.permissions.has(['MANAGE_MESSAGES', 'MANAGE_GUILD', 'MANAGE_CHANNELS', 'ADMINISTRATOR'])}**
        \`\`\`${message.content}\`\`\`
        `)
        .setColor('#303135')
        .setThumbnail(message.guild.iconURL({ dynamic: true }))
        if (channel) channel.send({embeds: [cmdlog]})
        return
      }
    }
  }

  const afk_check = await client.db.afk.findOne({ where: { guildID: message.guild.id, userID: message.author.id } })
  if (afk_check) {
    const afk_time = afk_check.time
    const time = humanizeDuration(afk_time - Date.now(), { round: true });
    client.db.afk.destroy({
      where: {
        guildID: message.guild.id,
        userID: message.author.id
      }
    })
    const embed = new MessageEmbed()
      .setDescription(`<:info:828536926603837441> **${message.author.tag}** welcome back! you were gone for **${time}**`)
      .setColor("#78c6fe");
    message.channel.send({ embeds: [embed] });
  } else if (message.mentions.members.first()) {
    const mention_check = await client.db.afk.findOne({ where: { guildID: message.guild.id, userID: message.mentions.members.first().id } })
    if (mention_check) {
      const embed = new MessageEmbed()
        .setDescription(`<:info:828536926603837441> **${message.mentions.members.first().user.tag}** is afk with the status: **${mention_check.content}**`)
        .setColor("#78c6fe");
      message.channel.send({ embeds: [embed] });
    }
  }
  const wf = db.get(`word_filter_${message.guild.id}_punish`)
  if (!message.member.permissions.has(['MANAGE_MESSAGES', 'MANAGE_GUILD', 'MANAGE_CHANNELS', 'ADMINISTRATOR']) && wf && wf.length && wf.some(x => message.content.toLowerCase().includes(x.split(' --')[0]))) {
    await message.delete()
    const punish = wf.filter(x => message.content.toLowerCase().includes(x.split(' --')[0]))
    const punishment = punish[0].split(' --')[1]
    const str = punish.toString().split(' --')[0]
    let arr = []
    str.split(' ').forEach(x => {
      arr.push(x.replace(x.charAt(x.length / x.length + 1), '#'))
    })
    let censored = arr.join(' ')
    if (punishment === 'mute') {
      const muteRoleId = await client.db.mute_role.findOne({ where: { guildID: message.guild.id } })
      const muterole = message.guild.roles.cache.get(muteRoleId.role)
      if (muterole) {
        const embed = new MessageEmbed()
          .setDescription(`<:mod:828541787801911327> ${message.member} (muted) Saying \`${censored}\` is prohibited here `)
          .setColor("#78c6fe");
        message.channel.send({ embeds: [embed] });
        client.utils.send_log_message(message, message.member, 'automod', `Member provided filtered word, and was muted.`)
        await message.member.roles.add(muterole)
      }
    } else if (punishment === 'ban') {
      const embed = new MessageEmbed()
        .setDescription(`<:mod:828541787801911327> ${message.member} (banned) Saying \`${censored}\` is prohibited here `)
        .setColor("#78c6fe");
      message.channel.send({ embeds: [embed] });
      client.utils.send_log_message(message, message.member, 'automod', `Member provided filtered word, and was banned.`)
      message.member.ban()
    } else if (punishment === 'kick') {
      const embed = new MessageEmbed()
        .setDescription(`<:mod:828541787801911327> ${message.member} (kicked) Saying \`${censored}\` is prohibited here `)
        .setColor("#78c6fe");
      message.channel.send({ embeds: [embed] });
      client.utils.send_log_message(message, message.member, 'automod', `Member provided filtered word, and was kicked.`)
      message.member.kick()
    } else if (punishment === 'delete') {
      const embed = new MessageEmbed()
        .setDescription(`<:mod:828541787801911327> ${message.member} (message deleted) Saying \`${censored}\` is prohibited here`)
        .setColor("#78c6fe");
      message.channel.send({ embeds: [embed] });
    }
  }
  const args = message.content.slice(message.author.username.length + 2).trim().split(' ');
  const custom_fm_check = await client.db.custom_fm.findOne({ where: { userID: message.author.id } })
  if (custom_fm_check && message.content.startsWith(message.author.username + 'fm')
    || message.content.startsWith(message.author.username + 'np')) client.commands.get('fm').run(message, args)
  const media = await client.db.media_channel.findOne({ where: { guildID: message.guild.id, channelID: message.channel.id } })
  if (media) {
    if (!message.attachments.first() && !message.member.permissions.has(['MANAGE_MESSAGES', 'MANAGE_GUILD', 'MANAGE_CHANNELS', 'ADMINISTRATOR'])) {
      message.delete()
    }
  }
}