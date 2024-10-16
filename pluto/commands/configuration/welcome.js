const { MessageEmbed, Permissions } = require('discord.js')
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')
const { EmbedBuilder } = require('../../utils/embedbuilder')

module.exports = {
  name: "welcome",
  aliases: ['welc'],
  description: `set up a welcome message for when new members join`,
  subcommands: '{guildprefix}welcome channel - set where to send welcome message\n{guildprefix}welcome message - edit the welcome message text\n{guildprefix}welcome test - test how the welcome message will look\n{guildprefix}welcome variables - list all the welcome message variables',
  usage: '{guildprefix}welcome',
  run: async(client, message, args) => {

    if(!message.member.permissions.has(Permissions.FLAGS.ADMINISTRATOR)) return message.channel.send(`this command requires \`administrator\` permission`)

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if (args[0] === 'channel') {

      if (args[1] === 'none') {

        const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

        if (globaldata.WelcomeChannel) {

          globaldata.WelcomeChannel = null;

          await globaldata.save();
          
          return message.channel.send('removed welcome channel 👍')     
        } else {
          return message.channel.send('there is no welcome channel') 
        }
        
      } else {

        const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

        const welcomechannel = message.mentions.channels.first() || client.guilds.cache.get(message.guild.id).channels.cache.get(args[1])

        if (!welcomechannel || welcomechannel.type !== 'GUILD_TEXT') {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setTitle(`${guildprefix}welcome channel`)
          .setDescription('set where to send welcome messages')
          .addFields(
          { name: '**usage**', value: `${guildprefix}welcome channel [channel]\n${guildprefix}welcome channel none`, inline: false },
          { name: '**aliases**', value: 'welc', inline: false },
          )

          return message.channel.send({ embeds: [embed] })
        }

        if (globaldata.WelcomeChannel) {

          globaldata.WelcomeChannel = welcomechannel.id;

          await globaldata.save();

          return message.channel.send(`i will send welcome messages to ${welcomechannel} from now on`)
        
        } else {

          globaldata.WelcomeChannel = welcomechannel.id;

          await globaldata.save();

          return message.channel.send(`i will send welcome messages to ${welcomechannel} from now on`)          
        }
      }

    } else if (args[0] === 'message') {

      const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

      if (!globaldata.WelcomeChannel) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setDescription(`this server doesnt have a welcome channel, assign one with \`${guildprefix}welcome channel\``)

        return message.channel.send({ embeds: [embed] })
        
      } else {

        const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
        
        const welcomemessage = args.splice(1).join(' ')

        let messagetoggle;

        if (globaldata.WelcomeMessage) {
          messagetoggle = globaldata.WelcomeMessage
        } else {
          messagetoggle = 'none'
        }

        if (!welcomemessage) {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`the current welcome message:\n\`\`\`${messagetoggle}\`\`\`\nto test it out use \`${guildprefix}welcome test\``)
          .setFooter({ text: `to disable the msg, use ${guildprefix}welcome channel none
to see all available variables, use ${guildprefix}welcome variables` })

          return message.channel.send({ embeds: [embed] })          
        }

        if (globaldata.WelcomeMessage) {

          new EmbedBuilder(message.channel, welcomemessage)

          globaldata.WelcomeMessage = welcomemessage;

          await globaldata.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`the welcome message was updated:\n\`\`\`${welcomemessage}\`\`\``)
          .setFooter({ text: `to disable the msg, use ${guildprefix}welcome channel none
to see all available variables, use ${guildprefix}welcome variables` })

          return message.channel.send({ embeds: [embed] })
        
        } else {

          new EmbedBuilder(message.channel, welcomemessage)

          globaldata.WelcomeMessage = welcomemessage;

          await globaldata.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`the welcome message was updated:\n\`\`\`${welcomemessage}\`\`\``)
          .setFooter({ text: `to disable the msg, use ${guildprefix}welcome channel none
to see all available variables, use ${guildprefix}welcome variables` })

          return message.channel.send({ embeds: [embed] })          
        }
      }

    } else if (args[0] === 'test') {

      const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

      if (!globaldata.WelcomeChannel) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setDescription(`you need to set a welcome channel first with \`${guildprefix}welcome channel\``)

        return message.channel.send({ embeds: [embed] })
        
      } else {

        const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

        let welcome = globaldata.WelcomeMessage

        let channelid = globaldata.WelcomeChannel

        welcome = welcome.replace('{user.mention}', message.member);
        welcome = welcome.replace('{user.name}', message.author.username);
        welcome = welcome.replace('{user.tag}', message.author.tag);
        welcome = welcome.replace('{user.id}', message.author.id);
        welcome = welcome.replace('{server.membercount}', message.member.guild.memberCount);
        const ordinal = (message.guild.memberCount.toString().endsWith(1) && !message.guild.memberCount.toString().endsWith(11)) ? 'st' : (message.guild.memberCount.toString().endsWith(2) && !message.guild.memberCount.toString().endsWith(12)) ? 'nd' : (message.guild.memberCount.toString().endsWith(3) && !message.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
        welcome = welcome.replace('{server.humanmembercount}', message.member.guild.memberCount + ordinal);
        welcome = welcome.replace('{server.name}', message.member.guild.name);

        var channel = message.guild.channels.cache.get(channelid)
        if (!channel) return;

        new EmbedBuilder(message.channel, welcome)
      }

    } else if (args[0] === 'variables') {

      const member = message.author

      const ordinal = (message.guild.memberCount.toString().endsWith(1) && !message.guild.memberCount.toString().endsWith(11)) ? 'st' : (message.guild.memberCount.toString().endsWith(2) && !message.guild.memberCount.toString().endsWith(12)) ? 'nd' : (message.guild.memberCount.toString().endsWith(3) && !message.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setDescription(`\`{user.id}\` — ${member.id}\n\`{user.name}\` — ${member.username}\n\`{user.mention}\` — ${member}\n\`{user.tag}\` — ${member.tag}\n\`{server.name}\` — ${message.guild.name}\n\`{server.membercount}\` — ${message.guild.memberCount}\n\`{server.humanmembercount}\` — ${message.member.guild.memberCount + ordinal}`)
    
      return message.channel.send({ embeds: [embed] })

    } else {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}welcome`)
      .setDescription('set up a welcome message for when new members join')
      .addFields(
      { name: '**subcommands**', value: `${guildprefix}welcome channel - set where to send welcome message\n${guildprefix}welcome message - edit the welcome message text\n${guildprefix}welcome test - test how the welcome message will look\n${guildprefix}welcome variables - list all the welcome message variables`, inline: false },
      { name: '**usage**', value: `${guildprefix}welcome`, inline: false },
      { name: '**aliases**', value: 'welc', inline: false },
      )

      return message.channel.send({ embeds: [embed] })  
    }
  }
}