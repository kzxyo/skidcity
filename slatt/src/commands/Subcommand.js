const {
  MessageEmbed
} = require('discord.js');
const permissions = require('../utils/json/permissions.json');

async function check(message) {
  const check = await message.client.db.updates.findOne({where: {guildID: message.guild.id}})
  if(!check && message.member.permissions.has('MANAGE_GUILD')) return true
  else return false
}

class Subcommand {
  constructor(client, options) {
    this.constructor.validateOptions(client, options);
    this.client = client;
    this.base = options.base;
    this.name = options.name;
    this.aliases = options.aliases || null;
    this.usage = options.usage || options.name;
    this.description = options.description || '';
    this.cooldown = options.cooldown || null;
    this.type = options.type || client.types.MISC;
    this.clientPermissions = options.clientPermissions || ['SEND_MESSAGES', 'EMBED_LINKS'];
    this.userPermissions = options.userPermissions || null;
    this.ownerOnly = options.ownerOnly || false;
    this.disabled = options.disabled || false;
    this.errorTypes = ['Invalid Argument', 'Subcommand Failure']
    this.hex = '#303135'
    this.config = require('../utils/json/config.json')
    this.support = 'https://discord.gg/47MH6nf26F'
    this.db = require('quick.db')
    this.functions = require('../utils/functions/functions.js')
    this.lastfm = require('../utils/functions/lastfm.js')
    this.embed = require('../utils/Embed.js')
  }

  checkPermissions(message, ownerOverride = true) {
    if (!message.channel.permissionsFor(message.guild.me).has(['SEND_MESSAGES', 'EMBED_LINKS'])) return false;
    const clientPermission = this.checkClientPermissions(message);
    const userPermission = this.checkUserPermissions(message, ownerOverride);
    if (clientPermission && userPermission) return true;
    else return false;
  }
  checkUserPermissions(message, ownerOverride = true) {
    if (!this.ownerOnly && !this.userPermissions) return true;
    if (ownerOverride && this.client.isOwner(message.author)) return true;
    if (this.ownerOnly && !this.client.isOwner(message.author)) {
      return false;
    }

    if (message.member.hasPermission('ADMINISTRATOR')) return true;
    if (this.userPermissions) {
      const missingPermissions =
        message.channel.permissionsFor(message.author).missing(this.userPermissions).map(p => permissions[p]);
      if (missingPermissions.length !== 0) {
        const embed = new MessageEmbed().setDescription(`> <:anti:828540580136484884> ${message.author} \`Missing Permissions:\` You need the **${missingPermissions.join(", ")}** permission${missingPermissions.length > 1 ? 's' : ''} to run \`${this.base} ${this.name}\``).setColor("eea62c")
        message.channel.send({embeds: [embed]})
        return false;
      }
    }
    return true;
  }
  checkClientPermissions(message) {
    const missingPermissions =
      message.channel.permissionsFor(message.guild.me).missing(this.clientPermissions).map(p => permissions[p]);
    if (missingPermissions.length !== 0) {
      const embed = new MessageEmbed().setDescription(`> <:anti:828540580136484884> ${message.author} \`Missing Permissions:\` I need the **${missingPermissions.join(", ")}** permission${missingPermissions.length > 1 ? 's' : ''} to run \`${this.base} ${this.name}\``).setColor("eea62c")
      message.channel.send({embeds: [embed]})
      return false;

    } else return true;
  }


  run(message, args) {
    throw new Error(`The ${this.name} command has no run() method`);
  }

  async send_error(message, errorType, errorMessage = null) {
    errorType = this.errorTypes[errorType];
    const embed = new MessageEmbed()
      .setDescription(`<:redx:827632831999246346> ${message.author} \`Error:\` ${errorMessage}`)
      .setColor("#990000");
      
    message.channel.send({ embeds: [embed] });
  }

  async api_error(message, api, error) {
    const embed = new MessageEmbed()
      .setDescription(`<:anti:828540580136484884> ${message.author} There was an unexpected error fetching info from the **${api}** API ${error !== undefined ? `- ${error}` : ''}`)
      .setColor("#eea62c");
      
    return message.channel.send({ embeds: [embed] });
  }


  async link_lastfm(message, user) {
    const prefix = message.prefix
    if (user.id !== message.member.id) {
      const embed = new MessageEmbed()
        .setDescription(`<:lastfm:794723149421871135> ${user}, Does not have a **Last.fm** name linked to their account, tell them to set it by using \`${prefix}lastfm set [username]\``)
        .setColor("#aa0000")
        
      return message.channel.send({ embeds: [embed] });
    }
    const embed = new MessageEmbed()
      .setDescription(`<:lastfm:794723149421871135> ${user}, Your **Last.fm** name is not linked to your account, you can set it by using \`${prefix}lastfm set [username]\``)
      .setColor("#aa0000")
      
    message.channel.send({ embeds: [embed] });
  }

  async send_info(message, infoMessage) {
    const embed = new MessageEmbed()
      .setDescription(`<:info:828536926603837441> ${message.author} ${infoMessage}`)
      .setColor("#78c6fe");
      
    message.channel.send({ embeds: [embed] });
  }

  async invalidUser(message) {
    const embed = new MessageEmbed()
      .setDescription(`<:anti:828540580136484884> ${message.author} \`Invalid User:\` The user you've provided is **invalid** try using a mention or id`)
      .setColor("eea62c");
      
    return message.channel.send({ embeds: [embed] });
  }

  async provideUser(message) {
    const embed = new MessageEmbed()
      .setDescription(`<:anti:828540580136484884> ${message.author} \`Invalid User:\` You must **provide a user** to run the **${this.name}** command`)
      .setColor("eea62c");
    return message.channel.send({ embeds: [embed] });
  }

  async invalidArgs(message, argsmessage) {
    const embed = new MessageEmbed()
      .setDescription(`<:anti:828540580136484884> ${message.author} \`Invalid Argument:\` ${argsmessage}`)
      .setColor("#eea62c");
      
    return message.channel.send({ embeds: [embed] });
  }

  async send_success(message, success = null) {
    const embed = new MessageEmbed()
      .setDescription(`<:success:827634903067394089> ${message.author} \`Success:\` ${success}`)
      .setColor("#007f00");
      
    message.channel.send({ embeds: [embed] });
  }

  prefix(message) {
    return message.prefix
  }

  async help(message) {
    const prefix = message.prefix
    let usage
    if (this.usage) usage = this.usage
    if (!this.usage) usage = 'None'
    let aliase
    if (this.aliases) aliase = this.aliases.join(', ')
    if (!this.aliases) aliase = 'None'
    const embed = new MessageEmbed()
      .setFooter(`Command Type: ${this.type} • Cooldown: ${this.cooldown || "None"} • do ${prefix}help ${this.base}`)
      .setTitle(`Subcommand`)
      .setAuthor('Command: ' + prefix + this.base)
      .setDescription(`\`\`\`
Usage: ${prefix}${usage}
  
Aliases: ${aliase}\`\`\``)
      .setColor(this.hex)
    if (this.userPermissions) embed.addField(`Permissions:`, `${this.userPermissions.join(', ') || "None"}`)
    if (!this.userPermissions) embed.addField(`Permissions:`, "None")
    message.channel.send({ embeds: [embed] })
  }

  static validateOptions(client, options) {
    if (!client) throw new Error('No client was found');
    if (typeof options !== 'object') throw new TypeError('Subcommand options is not an Object');
    if (typeof options.name !== 'string') throw new TypeError('Subcommand name is not a string');
    if (options.name !== options.name.toLowerCase()) throw new Error('Subcommand name is not lowercase');

    if (options.aliases) {
      if (!Array.isArray(options.aliases) || options.aliases.some(ali => typeof ali !== 'string'))
        throw new TypeError('Subcommand aliases is not an Array of strings');

      if (options.aliases.some(ali => ali !== ali.toLowerCase()))
        throw new RangeError('Subcommand aliases are not lowercase');

      for (const alias of options.aliases) {
        if (client.subcommand_aliases.get(alias)) throw new Error('Subcommand alias already exists');
      }
    }
    if (options.usage && typeof options.usage !== 'string') throw new TypeError('Subcommand usage is not a string');
    if (options.description && typeof options.description !== 'string')
      throw new TypeError('Subcommand description is not a string');
    if (options.type && typeof options.type !== 'string') throw new TypeError('Subcommand type is not a string');
    if (options.type && !Object.values(client.types).includes(options.type))
      throw new Error('Subcommand type is not valid');
    if (options.clientPermissions) {
      if (!Array.isArray(options.clientPermissions))
        throw new TypeError('Subcommand clientPermissions is not an Array of permission key strings');

      for (const perm of options.clientPermissions) {
        if (!permissions[perm]) throw new RangeError(`Invalid command clientPermission: ${perm}`);
      }
    }
    if (options.userPermissions) {
      if (!Array.isArray(options.userPermissions))
        throw new TypeError('Subcommand userPermissions is not an Array of permission key strings');

      for (const perm of options.userPermissions) {
        if (!permissions[perm]) throw new RangeError(`Invalid command userPermission: ${perm}`);
      }
    }
    if (options.subcommands && !Array.isArray(options.subcommands))
      throw new TypeError('Command subcommands is not an Array of permission key strings');
    if (options.ownerOnly && typeof options.ownerOnly !== 'boolean')
      throw new TypeError('Subcommand ownerOnly is not a boolean');
    if (options.disabled && typeof options.disabled !== 'boolean')
      throw new TypeError('Subcommand disabled is not a boolean');
  }
}

module.exports = Subcommand;