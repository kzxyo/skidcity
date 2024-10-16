const { MessageEmbed, Permissions } = require('discord.js')
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')
const autoresponderschema = require('../../database/autoresponder')

module.exports = {
  name: "autoresponder",
  aliases: ['ar', 'autoresponse', 'autorespond', 'trigger'],
  description: `automatically respond to specific triggers`,
  subcommands: '{guildprefix}autoresponder add - add a response trigger\n{guildprefix}autoresponder clear - remove all autoresponders\n{guildprefix}autoresponder list - list all response triggers\n{guildprefix}autoresponder remove - remove a response trigger',
  usage: '{guildprefix}autoresponder',
  run: async(client, message, args) => {

    if(!message.member.permissions.has(Permissions.FLAGS.ADMINISTRATOR)) return message.channel.send(`this command requires \`administrator\` permission`)

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if (args[0] === 'add' || args[0] === 'create') {

      const trigger = args[1]; 
    
      const response = args.slice(2).join(" ");

      if (!trigger) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}autoresponder add`)
        .setDescription(`add a response trigger`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}autoresponder add "trigger" hello world`, inline: false },
        { name: '**aliases**', value: `create`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })    
      }

      if (!response) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}autoresponder add`)
        .setDescription(`add a response trigger`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}autoresponder add "trigger" hello world`, inline: false },
        { name: '**aliases**', value: `create`, inline: false },
        )

        return message.channel.send({ embeds: [embed] }) 
      }


      const data = await autoresponderschema.findOne({ GuildID: message.guild.id, Trigger: trigger });

      if (data) {
        
        return message.channel.send(`an autoresponder for **${trigger}** already exists`)
        
      } else {

        const newdata = new autoresponderschema({
          GuildID: message.guild.id,
          Trigger: trigger,
          Response: response
        })
    
        await newdata.save();

        return message.channel.send(`created an autoresponder for **${trigger}** 👍`)
      }

    } else if (args[0] === 'clear') {

      const data = await autoresponderschema.findOne({ GuildID: message.guild.id })

      if (data) {

        await autoresponderschema.deleteMany({ GuildID: message.guild.id })

        return message.channel.send('removed all autoresponders 👍')

      } else {
        return message.channel.send('no autoresponders found')        
      }

    } else if (args[0] === 'list') {

      autoresponderschema.find({ GuildID: message.guild.id }, function(err, data) {

        if (data) {

          //let autoresponders = "";
          //data.forEach(guild => {
          //  autoresponders += `<@&${guild}>\n`;
          //});

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setTitle('autoresponders')
          .setDescription(`${data.map((cmd, i) => `**${i + 1}.** ${cmd.Trigger}: ${cmd.Response}`).slice(0, 30).join('\n') || 'there are no autoresponders set up'}`)
          //.setFooter({ text: `${autoresponders.length}` })
          
          return message.channel.send({ embeds: [embed] })
  
        } else {
          return message.channel.send('there are no autoresponders set up')
        }
      })

    } else if (args[0] === 'remove' || args[0] === 'delete' || args[0] === 'rm' || args[0] === 'del') {

      const name = args[1];

      if (!name) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}autoresponder remove`)
        .setDescription(`remove a response trigger`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}autoresponder remove [trigger]`, inline: false },
        { name: '**aliases**', value: `delete, rm, del`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })    
      }

      const data = autoresponderschema.findOne({ GuildID: message.guild.id, Trigger: name })

      if (data) {
      
        await autoresponderschema.findOneAndRemove({ GuildID: message.guild.id, Trigger: name });

        return message.channel.send(`removed the autoresponder for **${name}** 👍`)

      } else {
        return message.channel.send(`no autoresponder found for **${name}**`)
      }

    } else {
      
      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setTitle(`${guildprefix}autoresponder`)
      .setDescription('automatically respond to specific triggers')
      .addFields(
      { name: '**subcommands**', value: `${guildprefix}autoresponder add - add a response trigger\n${guildprefix}autoresponder clear - remove all autoresponders\n${guildprefix}autoresponder list - list all response triggers\n${guildprefix}autoresponder remove - remove a response trigger`, inline: false },
      { name: '**usage**', value: `${guildprefix}autoresponder`, inline: false },
      { name: '**aliases**', value: `ar, autoresponse, autorespond, trigger`, inline: false },
      )

      return message.channel.send({ embeds: [embed] })
    }
  }
}