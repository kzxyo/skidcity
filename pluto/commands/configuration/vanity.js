const { MessageEmbed, Permissions } = require('discord.js')
const { embedcolor, prefix } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "vanity",
  aliases: ['v'],
  description: `configurable settings to give roles when reppin vanity`,
  subcommands: '{guildprefix}vanity set- sets vanity\n{guildprefix}vanity role add - adds role to database\n{guildprefix}vanity role remove [role] - removes roles from database\n{guildprefix}vanity role clear - clears all roles in database\n{guildprefix}vanity message - set award message for vanity role\n{guildprefix}vanity variables - view variables for vanity role\n{guildprefix}vanity channel - sets vanity logs for guild\n{guildprefix}vanity settings - view settings for vanity role\n{guildprefix}vanity list - view vanity roles',
  usage: '{guildprefix}vanity',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({
      GuildID: message.guild.id,
    })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.ADMINISTRATOR)) return message.channel.send(`this command requires \`administrator\` permission`)

    if (args[0] === 'set') {

      if (args[1] === 'off') {

        const globaldata1 = await globaldataschema.findOne({
          GuildID: message.guild.id,
        });

        if (globaldata1.Vanity) {

          globaldata1.Vanity = null;

          await globaldata1.save();

          return message.channel.send(`vanity has been reset`)

        } else {

          return message.channel.send(`no vanity exists`)
        }

      } else {

        const vanitytext = args.splice(1).join(' ')

        if (!vanitytext) {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setTitle(`${guildprefix}vanity set`)
          .setDescription(`sets vanity`)
          .addFields(
          { name: '**usage**', value: `${guildprefix}vanity set`, inline: false },
          )

          return message.channel.send({ embeds: [embed] }) 
        }

        const globaldata2 = await globaldataschema.findOne({
          GuildID: message.guild.id,
        });

        if (globaldata2.Vanity) {
      
          globaldata2.Vanity = vanitytext

          await globaldata2.save();

          return message.channel.send(`set **${vanitytext}** as the vanity`)
      
        } else {

          globaldata2.Vanity = vanitytext

          await globaldata2.save();

          return message.channel.send(`set **${vanitytext}** as the vanity`)
        }
      }

    } else if (args[0] === 'role') {

      if (args[1] === 'add') {

        const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[2])
    
        if (!role) return message.channel.send(`i couldn't find that role`)

        globaldataschema.findOne({ GuildID: message.guild.id }, async function(err, data) {

          if (data?.VanityRoles.includes(role.id)) {

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setDescription(`${role} is already a vanity role`)

            return message.channel.send({ embeds: [embed] })   
    
          } else {

            data.VanityRoles.push(role.id)
            data.save();

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setDescription(`${role} is now a vanity role`)

            return message.channel.send({ embeds: [embed] })     
          }
        })

      } else if (args[1] === 'remove') {

        const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[2])
    
        if (!role) return message.channel.send(`i couldn't find that role`)

        globaldataschema.findOne({ GuildID: message.guild.id }, async function(err, data) {

          if (!data?.VanityRoles.includes(role.id)) {

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setDescription(`${role} does not exist as a vanity role`)

            return message.channel.send({ embeds: [embed] })     
          }

          let i = data.VanityRoles.indexOf(`${role.id}`)
          data.VanityRoles.splice(i, 1)
          data.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`${role} is now removed as a vanity role`)

          return message.channel.send({ embeds: [embed] })
        })

      } else if (args[1] === 'clear') {

        const globaldata3 = await globaldataschema.findOne({
          GuildID: message.guild.id,
        });

        const array = globaldata3.VanityRoles

        if (array.length > 0) {

          globaldata3.VanityRoles = [];

          await globaldata3.save();

          return message.channel.send(`vanity roles cleared`)
          
        } else {

          return message.channel.send(`no vanity roles exist`)
        }

      } else {

        return message.channel.send(`you can only **add**, **remove** or **clear** roles`)     
      }

    } else if (args[0] === 'message') {

      if (args[1] === 'off') {

        const globaldata = await globaldataschema.findOne({
          GuildID: message.guild.id,
        });

        if (globaldata.VanityMessage) {

          globaldata.VanityMessage = null;

          await globaldata.save();

          return message.channel.send(`vanity message has been reset`)

        } else {

          return message.channel.send(`no vanity message exists`)
        }

      } else {

        const vanitymessage = args.splice(1).join(' ')

        if (!vanitymessage) {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setTitle(`${guildprefix}vanity message`)
          .setDescription(`set award message for vanity role`)
          .addFields(
          { name: '**usage**', value: `${guildprefix}vanity message [msg]`, inline: false },
          )

          return message.channel.send({ embeds: [embed] })
        }

        const globaldata1 = await globaldataschema.findOne({
          GuildID: message.guild.id,
        });

        if (globaldata1.VanityMessage) {

          globaldata.VanityMessage = vanitymessage;

          await globaldata.save();
          
          return message.channel.send(`set **${vanitymessage}** as vanity message`)

        } else {

          globaldata.VanityMessage = vanitymessage;

          await globaldata.save();

          return message.channel.send(`set **${vanitymessage}** as vanity message`)
        }
      }

    } else if (args[0] === 'variables') {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setDescription(`\`{user.mention}\` ＊ ${message.member}\n\`{user.name}\` ＊ ${message.author.username}\n\`{user.tag}\` ＊ ${message.author.tag}\n\`{user.id}\` ＊ ${message.author.id}\n\`{server.name}\` ＊ ${message.guild.name}`)

      return message.channel.send({ embeds: [embed] })

    } else if (args[0] === 'channel') {

      if (args[1] === 'off') {

        const globaldata = await globaldataschema.findOne({
          GuildID: message.guild.id,
        });

        if (globaldata.VanityLogChannel) {

          globaldata.VanityLogChannel = null;

          await globaldata.save();

          return message.channel.send(`vanity logchannel has been reset`)

        } else {

          return message.channel.send(`no vanity logchannel exists`)
        }

      } else {

        const globaldata1 = await globaldataschema.findOne({
          GuildID: message.guild.id,
        });

        const logchannel = message.mentions.channels.first() || client.guilds.cache.get(message.guild.id).channels.cache.get(args[1])

        if (!logchannel || logchannel.type !== 'GUILD_TEXT' && logchannel.type !== 'GUILD_NEWS') {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setTitle(`${guildprefix}vanity channel [channel/off]`)
          .setDescription(`sets vanity logs`)
          .addFields(
          { name: '**usage**', value: `${guildprefix}vanity channel [channel/off]`, inline: false },
          )

          return message.channel.send({ embeds: [embed] })
        }

        if (globaldata1.VanityLogChannel) {

          globaldata.VanityLogChannel = logchannel.id;

          await globaldata.save();
  
          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`set ${logchannel} as vanity logchannel`)

          return message.channel.send({ embeds: [embed] })

        } else {

          globaldata.VanityLogChannel = logchannel.id;

          await globaldata.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`set ${logchannel} as vanity logchannel`)

          return message.channel.send({ embeds: [embed] })
        } 
      }

    } else if (args[0] === 'settings') {

      const globaldata = await globaldataschema.findOne({
        GuildID: message.guild.id,
      });

      let vanitytoggle;

      if (globaldata.Vanity) {
        vanitytoggle = globaldata.Vanity    
      } else {
        vanitytoggle = '\`none\`'       
      }

      let vanitymessagetoggle;

      if (globaldata.VanityMessage) {
        vanitymessagetoggle = globaldata.VanityMessage    
      } else {
        vanitymessagetoggle = '\`none\`'       
      }

      let vanitylogchannel;

      if (globaldata.VanityLogChannel) {
        vanitylogchannel = `<#${globaldata.VanityLogChannel}>`   
      } else {
        vanitylogchannel = '\`none\`'       
      }

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle('vanity settings')
      //.setDescription(`vanity: **${vanitytoggle}**\nmessage: **${vanitymessagetoggle}**\nlog channel: ${vanitylogchannel}`)
      .addFields(
      { name: '**vanity**', value: `${vanitytoggle}`, inline: false },
      { name: '**message**', value: `${vanitymessagetoggle}`, inline: false },
      { name: '**log channel**', value: `${vanitylogchannel}`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })

    } else if (args[0] === 'list') {

      const globaldata3 = await globaldataschema.findOne({
        GuildID: message.guild.id,
      });

      const array = globaldata3.VanityRoles

      let roles = "";
      array.forEach(guild => {
        roles += `<@&${guild}>\n`;
      });

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle('vanity roles')
      .setDescription(roles.length ? `${roles}` : "\`none\`")

      return message.channel.send({ embeds: [embed] }) 

    } else {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}vanity`)
      .setDescription('configurable settings to give roles when reppin vanity')
      .addFields(
      { name: '**subcommands**', value: `${guildprefix}vanity set - sets vanity\n${guildprefix}vanity role add - adds role to database\n${guildprefix}vanity role remove - removes roles from database\n${guildprefix}vanity role clear - clears all roles in database\n${guildprefix}vanity message - set award message for vanity role\n${guildprefix}vanity variables - view variables for vanity role\n${guildprefix}vanity channel - sets vanity logs for guild\n${guildprefix}vanity settings - view settings for vanity role\n${guildprefix}vanity list - view vanity roles`, inline: false },
      { name: '**usage**', value: `${guildprefix}vanity`, inline: false },
      { name: '**aliases**', value: 'v', inline: false },
      )

      return message.channel.send({ embeds: [embed] })  
    }
  }
}