const Command = require('../Command.js');
const {
  MessageEmbed
} = require('discord.js');
const helppgn = require('../helppgn.js');
const ReactionMenu = require('../ReactionMenu.js');
const Discord = require('discord.js');

module.exports = class HelpCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'help',
      aliases: ['commands', 'cmds'],
      usage: 'help [command]',
      description: 'displays a total list of commands, and some precise command info',
      type: client.types.INFO,
      subcommands: ['help ping']
    });
  }
  async run(message, args) {
    const { stripIndent } = require('common-tags')
    const embed = new MessageEmbed()
    const prefix = message.prefix
    const {
      OWNER
    } = message.client.types;
    let Types
    if (message.client.isOwner(message.member)) {
      Types = Object.values(message.client.types)
    } else {
      Types = Object.values(message.client.types).filter(x => x !== 'owner')
    }
    if (args.length === 1) {
      if (Types.some(x => x === args[0].toLowerCase())) {
        const type = Types.filter(x => x.toLowerCase() === args[0].toLowerCase())[0]
        let num = 0
        const Commands = []
        message.client.commands.forEach(x => {
          if (x.type === type) Commands.push(x)
        })
        message.client.subcommands.forEach(x => {
          if (x.type === type) Commands.push(x)
        })
        const list = Commands.map(x => `\`${++num}\` **${x.base ? x.base : ''} ${x.name}** - ${x.description}`)
        const embed = new MessageEmbed()
          .setAuthor(message.author.username, message.author.avatarURL({ dynamic: true }))
          .setTitle(`Commands for **${type}**`)
          .setDescription(list.join('\n'))
          .setColor(this.hex)
          .setFooter(`${list.length} commands for ${type}`)
        if (list.length <= 10) {
          message.channel.send({ embeds: [embed] })
        } else {
          new ReactionMenu(message.client, message.channel, message.member, embed, list);
        }
        return
      }
      const command = message.client.commands.get(args[0].toLocaleLowerCase()) || message.client.aliases.get(args[0].toLocaleLowerCase())
      if (command && (command.type != OWNER || message.client.isOwner(message.member))) {
        let subcommands
        const find_subcmd = message.client.subcommands.filter(c => c.base === command.name)
        if (find_subcmd) subcommands = find_subcmd.map(c => `${prefix}${c.base} ${c.name} - ${c.description}`)
        if (subcommands.length > 0) embed.addField(`Subcommands`, subcommands.join('\n'))
        if (command.description) embed.setDescription(command.description);
        if (command.aliases) embed.addField(`${message.client.emotes.search} Aliases`, command.aliases.map(c => `${c}`).join(', '), false);
        if (command.usage) embed.addField(`${message.client.emotes.server} Usage`, `${prefix}${command.usage}`, false)
        if (command.userPermissions) embed.addField(`${message.client.emotes.mod} Permissions`, command.userPermissions.map(c => `${c}`).join(', '), false)
        embed
          .setColor(this.hex)
          .setFooter(`${subcommands.length > 1 ? `${subcommands.length} subcommands ·` : ''} Category: ${command.type}`)
          .setTitle(`${command.name} ${subcommands.length > 0 ? '(subcommands)' : ''}`)
          .setAuthor(`${message.client.user.username}`, message.client.user.avatarURL())
        if (subcommands.length <= 5) {
          return message.channel.send({ embeds: [embed] })
        } else {
          new helppgn(message.client, message.channel, message.member, command, prefix, embed, subcommands);
        }
      } else {
        return this.send_error(message, 0, `**${args[0]}** is not a valid command, or type. Use \`${prefix}help\` for a list`)
      }
    } else if (args[1]) {
      const cmd = message.client.commands.get(args[0].toLowerCase()) || message.client.aliases.get(args[0].toLowerCase())
      if (!cmd) return this.send_error(message, 0, `**${args[0]}** is not a valid command, or type. Use \`${prefix}help\` for a list`)
      const input = cmd.name + ' ' + args[1].toLowerCase()
      const subcommand =
        message.client.subcommands.get(input)
        || message.client.subcommand_aliases.get(input)
      if (!subcommand) return this.send_error(message, 0, `**${args.join(' ')}** is not a valid subcommand, command, or type. Use \`${prefix}help\` for a list`)
      if (subcommand && subcommand.type != OWNER || message.client.isOwner(message.member)) {
        embed.setAuthor(`${message.client.user.username}`, message.client.user.avatarURL())
          .setTitle(`Subcommand: ${subcommand.base} ${subcommand.name}`)
          .setFooter(`Base command: ${subcommand.base} · Category: ${subcommand.type}`)
        embed.setColor(this.hex);
        if (subcommand.description) embed.setDescription(subcommand.description)
        if (subcommand.aliases) embed.addField(`${message.client.emotes.search} Aliases`, subcommand.aliases.map(c => `${c}`).join(', '));
        if (subcommand.usage) embed.addField(`${message.client.emotes.server} Usage`, `${prefix}${subcommand.usage}`)
        if (subcommand.userPermissions) embed.addField(`${message.client.emotes.mod} Permissions`, subcommand.userPermissions.map(c => `${c}`).join(', '), false)
        return message.channel.send({ embeds: [embed] })
      } else {

      }
    } else if (args.length === 0) {
      const updates = await message.client.db.updates.findOne({ where: { guildID: message.guild.id } })
      embed.setAuthor(message.author.username, message.author.avatarURL({ dynamic: true }))
        .setTitle(`Help`)
        .setDescription(stripIndent`
        ${updates === null && message.member.permissions.has('MANAGE_GUILD') ? "<:anti:828540580136484884> **Updates channel not set! Please use the 'updates' command** <:anti:828540580136484884>" : ""}
         View **[updates](https://commands.slatt.gay/bot/recent-updates)** for new features
        Use **${message.prefix}help <command name>**
        Or **${message.prefix}help <type>**
        \`\`\`Info      |   Mod
        Fun       |   Server
        Lastfm    |   Search\`\`\`
        `)
        .setColor(this.hex)
        let row = new Discord.MessageActionRow()
    row.addComponents(new Discord.MessageButton()
      .setURL(`https://discord.com/api/oauth2/authorize?client_id=${message.client.user.id}&permissions=8&scope=bot`)
      .setLabel(`Invite`)
      .setStyle(`LINK`)
      .setEmoji(`${message.client.emotes.info}`))
    row.addComponents(new Discord.MessageButton()
      .setURL('https://slatt.gitbook.io/slatt-help/')
      .setLabel(`Commands`)
      .setStyle(`LINK`)
      .setEmoji(`${message.client.emotes.mod}`))
      message.channel.send({ embeds: [embed], components: [row] });
    }
  }
};