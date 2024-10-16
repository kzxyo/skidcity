const { MessageEmbed, Permissions } = require('discord.js')
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')
const { EmbedBuilder } = require('../../utils/embedbuilder')

module.exports = {
  name: "goodbye",
  description: `set up a goodbye message for when members leave`,
  subcommands: '{guildprefix}goodbye channel - set where to send goodbye  messages\n{guildprefix}goodbye  message - edit the goodbye message text\n{guildprefix}goodbye  test - test how the goodbye message will look\n{guildprefix}goodbye variables - list all the goodbye message variables',
  usage: '{guildprefix}goodbye',
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

        if (globaldata.GoodbyeChannel) {

          globaldata.GoodbyeChannel = null;

          await globaldata.save();
          
          return message.channel.send('removed goodbye channel 👍')     
        } else {
          return message.channel.send('there is no goodbye channel') 
        }
        
      } else {

        const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

        const goodbyechannel = message.mentions.channels.first() || client.guilds.cache.get(message.guild.id).channels.cache.get(args[1])

        if (!goodbyechannel || goodbyechannel.type !== 'GUILD_TEXT') {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setTitle(`${guildprefix}goodbye channel`)
          .setDescription('set where to send goodbye messages')
          .addFields(
          { name: '**usage**', value: `${guildprefix}goodbye channel [channel]\n${guildprefix}goodbye channel none`, inline: false },
          )

          return message.channel.send({ embeds: [embed] })
        }

        if (globaldata.GoodbyeChannel) {

          globaldata.GoodbyeChannel = goodbyechannel.id;

          await globaldata.save();

          return message.channel.send(`i will send goodbye messages to ${goodbyechannel} from now on`)
        
        } else {

          globaldata.GoodbyeChannel = goodbyechannel.id;

          await globaldata.save();

          return message.channel.send(`i will send goodbye messages to ${goodbyechannel} from now on`)          
        }
      }

    } else if (args[0] === 'message') {

      const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

      if (!globaldata.GoodbyeChannel) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setDescription(`this server doesnt have a goodbye channel, assign one with \`${guildprefix}goodbye channel\``)

        return message.channel.send({ embeds: [embed] })
        
      } else {

        const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
        
        const goodbyemessage = args.splice(1).join(' ')

        let messagetoggle;

        if (globaldata.WelcomeMessage) {
          messagetoggle = globaldata.GoodbyeMessage
        } else {
          messagetoggle = 'none'
        }

        if (!goodbyemessage) {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`the current goodbye message:\n\`\`\`${messagetoggle}\`\`\`\nto test it out use \`${guildprefix}goodbye test\``)
          .setFooter({ text: `to disable the msg, use ${guildprefix}goodbye channel none
to see all available variables, use ${guildprefix}goodbye variables` })

          return message.channel.send({ embeds: [embed] })          
        }

        if (globaldata.GoodbyeMessage) {

          new EmbedBuilder(message.channel, goodbyemessage)

          globaldata.GoodbyeMessage = goodbyemessage;

          await globaldata.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`the goodbye message was updated:\n\`\`\`${goodbyemessage}\`\`\``)
          .setFooter({ text: `to disable the msg, use ${guildprefix}goodbye channel none
to see all available variables, use ${guildprefix}goodbye variables` })

          return message.channel.send({ embeds: [embed] })
        
        } else {

          new EmbedBuilder(message.channel, goodbyemessage)

          globaldata.GoodbyeMessage = goodbyemessage;

          await globaldata.save();

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`the goodbye message was updated:\n\`\`\`${goodbyemessage}\`\`\``)
          .setFooter({ text: `to disable the msg, use ${guildprefix}goodbye channel none
to see all available variables, use ${guildprefix}goodbye variables` })

          return message.channel.send({ embeds: [embed] })          
        }
      }

    } else if (args[0] === 'test') {

      const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

      if (!globaldata.GoodbyeChannel) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setDescription(`you need to set a goodbye channel first with \`${guildprefix}goodbye channel\``)

        return message.channel.send({ embeds: [embed] })
        
      } else {

        const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

        let goodbye = globaldata.GoodbyeMessage

        let channelid = globaldata.GoodbyeChannel

        goodbye = goodbye.replace('{user.mention}', message.member);
        goodbye = goodbye.replace('{user.name}', message.author.username);
        goodbye = goodbye.replace('{user.tag}', message.author.tag);
        goodbye = goodbye.replace('{user.id}', message.author.id);
        goodbye = goodbye.replace('{server.membercount}', message.member.guild.memberCount);
        const ordinal = (message.guild.memberCount.toString().endsWith(1) && !message.guild.memberCount.toString().endsWith(11)) ? 'st' : (message.guild.memberCount.toString().endsWith(2) && !message.guild.memberCount.toString().endsWith(12)) ? 'nd' : (message.guild.memberCount.toString().endsWith(3) && !message.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
        goodbye = goodbye.replace('{server.humanmembercount}', message.member.guild.memberCount + ordinal);
        goodbye = goodbye.replace('{server.name}', message.member.guild.name);

        var channel = message.guild.channels.cache.get(channelid)
        if (!channel) return;

        new EmbedBuilder(message.channel, goodbye)
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
      .setTitle(`${guildprefix}goodbye`)
      .setDescription('set up a goodbye message for when members leave')
      .addFields(
      { name: '**subcommands**', value: `${guildprefix}goodbye channel - set where to send goodbye  messages\n${guildprefix}goodbye  message - edit the goodbye message text\n${guildprefix}goodbye  test - test how the goodbye message will look\n${guildprefix}goodbye variables - list all the goodbye message variables`, inline: false },
      { name: '**usage**', value: `${guildprefix}goodbye`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })  
    }
  }
}