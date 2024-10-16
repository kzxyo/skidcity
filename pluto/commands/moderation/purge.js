const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "purge",
  aliases: ['p', 'prune', 'clean', 'clear'],
  description: `bulk delete messages from a channel`,
  subcommands: `{guildprefix}purge bots - purges messages that are from bots\n{guildprefix}purge contains - purge messages that contain some text\n{guildprefix}purge embeds - purge messages that contain embeds\n{guildprefix}purge startsWith - purge messages that start with some text\n{guildprefix}purge endsWith - purge messages that end with some text\n{guildprefix}purge humans - purge messages that are from humans\n{guildprefix}purge not - purge messages that don't contain some text\n{guildprefix}purge user - purge up to 100 messages at once from a specific user\n{guildprefix}purge mentions - purge mentions\n{guildprefix}purge links - purge links that were sent\n{guildprefix}purge invites - purge invite links that were sent\n{guildprefix}purge attachments - purge images that were sent`,
  usage: '{guildprefix}purge',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires \`manage messages\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires me to have \`manage messages\` permission`)

    if (args[0] === 'bots') {

      const number = args[1]

      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge bots`)
        .setDescription('purge messages that contain bots')
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge bots [amount]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(msg => msg.author.bot)

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered by bots`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} bot messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else if (args[0] === 'contains') {

      const number = args[1]

      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge contains`)
        .setDescription('purge messages that contains')
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge contains [amount] [text]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      const text = args[2];

      if(text) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a word`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(m => m.content.includes(text))

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered that contains **${text}**`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else if (args[0] === 'embeds') {

      const number = args[1]

      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge embeds`)
        .setDescription('purge messages that contain embeds')
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge embeds [amount]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(m => m.embeds.length)

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered by embeds`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else if (args[0] === 'startsWith') {

      const number = args[1]

      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge startsWith`)
        .setDescription('purge messages that startsWith')
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge startsWith [amount] [text]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      const text = args[2];

      if(text) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a word`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(m => m.content.startsWith(text))

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered that starts with **${text}**`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else if (args[0] === 'endsWith') {

      const number = args[1]

      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge endsWith`)
        .setDescription('purge messages that endsWith')
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge endsWith [amount] [text]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      const text = args[2];

      if(text) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a word`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(m => m.content.endsWith(text))

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered that ends with **${text}**`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else if (args[0] === 'humans') {

      const number = args[1]

      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge humans`)
        .setDescription('purge messages that contain humans')
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge humans [amount]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(m => !m.author.bot)

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered by humans`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else if (args[0] === 'not') {

      const number = args[1];

      const text = args.slice(2).join(" ");

      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge not`)
        .setDescription(`purge messages that don't contain some text`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge not [amount]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if (!text) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a text`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(m => !m.content.includes(text))

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered not containing **${text}**`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else if (args[0] === 'user') {

      const user = message.mentions.members.first() || message.guild.members.cache.get(args[1]);

      const number = args[2];

      if(!user) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge user`)
        .setDescription('purge up to 100 messages at once from a specific user')
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge user [amount]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(x => x.author.id === user.id)

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered by ${user}`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else if (args[0] === 'mentions') {

      const number = args[1]

      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge mentions`)
        .setDescription('purge messages that contain mentions')
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge mentions [amount]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(m => m.mentions.users.size > 0)

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered by mentions`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else if (args[0] === 'links') {

      const number = args[1]

      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge links`)
        .setDescription('purge messages that contain links')
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge links [amount]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(m => m.content.startsWith('http') || m.content.startsWith('https') || m.content.includes('https'))

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered by links`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else if (args[0] === 'invites') {

      const number = args[1]

      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge invites`)
        .setDescription('purge messages that contain invites')
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge invites [amount]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(m => m.content.startsWith('http') || m.content.startsWith('discord.gg/') || m.content.includes('discord.gg'))

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered by invites`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else if (args[0] === 'attachments') {

      const number = args[1]

      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge attachments`)
        .setDescription('purge messages that contain attachments')
        .addFields(
        { name: '**usage**', value: `${guildprefix}purge attachments [amount]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })  
      }

      if(number < 1) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      if(number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(m => m.attachments.first)

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found filtered by attachments`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          return message.channel.send(`purged ${messages.size} messages 👍`)

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }

    } else {

      if (!args[0]) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}purge`)
        .setDescription('bulk delete messages from a channel')
        .addFields(
        { name: '**subcommands**', value: `${guildprefix}purge bots - purges messages that are from bots\n${guildprefix}purge contains - purge messages that contain some text\n${guildprefix}purge embeds - purge messages that contain embeds\n${guildprefix}purge startsWith - purge messages that start with some text\n${guildprefix}purge endsWith - purge messages that end with some text\n${guildprefix}purge humans - purge messages that are from humans\n${guildprefix}purge not - purge messages that don't contain some text\n${guildprefix}purge user - purge up to 100 messages at once from a specific user\n${guildprefix}purge mentions - purge mentions\n${guildprefix}purge links - purge links that were sent\n${guildprefix}purge invites - purge invite links that were sent\n${guildprefix}purge attachments - purge images that were sent`, inline: false },
        { name: '**usage**', value: `${guildprefix}purge\n${guildprefix}purge @remorseful 50`, inline: false },
        { name: '**aliases**', value: `p, prune, clean, clear`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(mem => mem.user.username === args[0]) || message.guild.members.cache.find(mem => mem.user.tag === args[0])

      if (!user) {

        const number = args[0];
    
        if(isNaN(number)) {

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`you can only provide numbers`)

          return message.channel.send({ embeds: [embed] })
        }

        if(number < 1 || number > 99) {

          const embed = new MessageEmbed()
        
          .setColor(embedcolor)
          .setDescription(`provide a number between 1 and 100`)
            
          return message.channel.send({ embeds: [embed] })
        }

        message.channel.bulkDelete(number, true).then(() => {
          message.delete().catch(() => { return; })
        }).catch(() => { return; })
      } else {

      const number = args[1];
    
      if(isNaN(number)) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setDescription(`you can only provide numbers`)

        return message.channel.send({ embeds: [embed] })
      }

      if(number < 1 || number > 99) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`provide a number between 1 and 100`)
            
        return message.channel.send({ embeds: [embed] })
      }

      let messages = await message.channel.messages.fetch({ limit: number })
      let filteredmessages = await messages.filter(x => x.author.id === user.id)

      if (filteredmessages.size === 0) {

        const embed = new MessageEmbed()
        
        .setColor(embedcolor)
        .setDescription(`no messages found from ${user}`)
            
        return message.channel.send({ embeds: [embed] })

      } else {

        message.channel.bulkDelete(filteredmessages, true).then(messages => {

          message.delete().catch(() => { return; })

          const embed = new MessageEmbed()

          .setColor(embedcolor)
          .setDescription(`purge **${messages.size}** messages from ${user}`)

          return message.channel.send({ embeds: [embed] }).then((msg) => {
            setTimeout(() => msg.delete().catch(() => { return; }), 2000);
          })

        }).catch(() => {
          return message.channel.send('an error occured')       
        })
      }
      }
    } 
  }
}