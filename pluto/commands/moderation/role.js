const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "role",
  description: `add/remove a role from a member`,
  subcommands: '{guildprefix}role add - add a role to a member\n{guildprefix}role color - change the color of a role\n{guildprefix}role create - create a new role\n{guildprefix}role delete - delete a role\n{guildprefix}role remove - remove a role from a member\n{guildprefix}role rename - change the name of a role\n{guildprefix}role toggle - add/remove a role from a member',
  usage: '{guildprefix}role add [member] [role]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })

    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send(`this command requires \`manage roles\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_ROLES)) return message.channel.send(`this command requires me to have \`manage roles\` permission`)

    if (args[0] === 'add') {

      const user = message.mentions.members.first() || message.guild.members.cache.get(args[1]);

      const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[2]) || message.guild.roles.cache.find(r => r.name.toLowerCase() === args.slice(2).join(' ').toLocaleLowerCase());

      if (!user) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}role add`)
        .setDescription(`add a role to a member`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}role add [member] [role]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      if (!role) return message.channel.send(`i couldn't find that role`)

      if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send(`this user has a higher role than you`)

      if (role.position >= client.user.roles?.highest.position) return message.channel.send(`i can't give this role it's higher than mine`)

      if (role.position >= message.member.roles.highest.position) return message.channel.send(`you can't give this role as it's higher than you`)

      user.roles.add(role.id).then(() => {
        return message.channel.send(`added **${role.name}** to **${user.user.tag}** 👍`)
      }).catch(() => {
        return message.channel.send(`an error occured`)
      })

    } else if (args[0] === 'color') {

      const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1]);

      const color = args[2]

      if (!role) return message.channel.send(`i couldn't find that role`)

      if (!color) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}role color`)
        .setDescription(`change the color of a role`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}role color [role] [color]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      if (role.position >= client.user.roles?.highest.position) return message.channel.send(`i can't color this role as it's higher than mine`)

      if (role.position >= message.member.roles.highest.position) return message.channel.send(`you can't color a role that's higher than mine`)

      role.setColor(color).then(() => {
        return message.channel.send(`changed the color for **${role.name}** to **${color}**`)
      }).catch(() => {
        return message.channel.send(`an error occured`)
      })

    } else if (args[0] === 'create') {

      const rolename = args.splice(1).join(' ')

      if (!rolename) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}role create`)
        .setDescription(`create a new role`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}role create [name]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      message.guild.roles.create({
        name: rolename,
      }).then(() => {
        return message.channel.send(`created a role named **${rolename}** 👍`)
      }).catch(() => {
        return message.channel.send(`an error occured`)
      })

    } else if (args[0] === 'delete') {

      const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1]);

      if (!role) return message.channel.send(`i couldn't find that role`)

      if (role.position >= client.user.roles?.highest.position) return message.channel.send(`i can't give this role it's higher than mine`)

      if (role.position >= message.member.roles.highest.position) return message.channel.send(`im unable to delete a role higher than mine`)

      role.delete().then(() => {
        return message.channel.send(`**${role.name}** has been deleted 👍`)
      }).catch(() => {
        return message.channel.send(`an error occured`)
      })    

    } else if (args[0] === 'remove'  || args[0] === 'rm') {

      const user = message.mentions.members.first() || message.guild.members.cache.get(args[1]);;

      const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[2])

      if (!user) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}role remove`)
        .setDescription(`remove a role from a member`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}role remove [member] [role]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      if (!role) return message.channel.send(`i couldn't find that role`)

      if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send(`this user has a higher role than you`)

      if (role.position >= client.user.roles?.highest.position) return message.channel.send(`i can't remove this role it's higher than mine`)

      user.roles.remove(role.id).then(() => {
        return message.channel.send(`removed **${role.name}** from **${user.user.tag}** 👍`)
      }).catch(() => {
        return message.channel.send(`an error occured`)
      })

    } else if (args[0] === 'rename') {

      const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1])

      const rolename = args.splice(2).join(' ')

      if (!role) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}role rename`)
        .setDescription(`change the name of a role`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}role rename [role] [name]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      if (!rolename) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}role rename`)
        .setDescription(`change the name of a role`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}role rename [role] [name]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      if (role.position >= client.user.roles?.highest.position) return message.channel.send(`i can't rename this role it's higher than mine`)

      if (role.position >= message.member.roles.highest.position) return message.channel.send(`you can't rename this role as it's higher than you`)

      role.setName(rolename).then(() => {
        return message.channel.send(`changed **${role.name}** to **${rolename}** 👍`)
      }).catch(() => {
        return message.channel.send(`an error occured`)
      })
      
    } else if (args[0] === 'toggle') {

      const user = message.mentions.members.first() || message.guild.members.cache.get(args[1]);;

      const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[2])

      if (!user) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}role remove`)
        .setDescription(`remove a role from a member`)
        .addFields(
        { name: '**usage**', value: `${guildprefix}role remove [member] [role]`, inline: false },
        )

        return message.channel.send({ embeds: [embed] })
      }

      if (!role) return message.channel.send(`i couldn't find that role`)

      if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send(`this user has a higher role than you`)

      if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send(`this user has a higher role than you`)

      if (role.position >= client.user.roles?.highest.position) return message.channel.send(`i can't remove this role it's higher than mine`)

      if (user.roles.cache.has(role.id)) {

        user.roles.remove(role.id).then(() => {
          return message.channel.send(`removed **${role.name}** from **${user.user.tag}** 👍`)
        }).catch(() => {
          return message.channel.send(`an error occured`)
        })
        
      } else {

        user.roles.add(role.id).then(() => {
          return message.channel.send(`added **${role.name}** to **${user.user.tag}** 👍`)
        }).catch(() => {
          return message.channel.send(`an error occured`)
        }) 
      }

    } else {

      const user = message.mentions.members.first() || message.guild.members.cache.get(args[0]);

      const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1]) || message.guild.roles.cache.find(r => r.name.toLowerCase() === args.slice(1).join(' ').toLowerCase()) || message.guild.roles.cache.find(r => r.name.includes(args.slice(1).join(' ').toLowerCase()))

      if (!user) {

        const embed = new MessageEmbed()
    
        .setColor(embedcolor)
        .setTitle(`${guildprefix}role`)
        .setDescription(`add/remove a role from a member`)
        .addFields(
        { name: '**subcommands**', value: `${guildprefix}role add - add a role to a member\n${guildprefix}role color - change the color of a role\n${guildprefix}role create - create a new role\n${guildprefix}role delete - delete a role\n${guildprefix}role remove - remove a role from a member\n${guildprefix}role rename - change the name of a role\n${guildprefix}role toggle - add/remove a role from a member`, inline: false },
        { name: '**usage**', value: `${guildprefix}role add [member] [role]`, inline: false },
        )
    
        return message.channel.send({ embeds: [embed] })
      }

      if (!role) return message.channel.send(`i couldn't find that role`)

      if (user.roles.highest.position >= message.member.roles.highest.position) return message.channel.send(`this user has a higher role than you`)

      if (role.position >= client.user.roles?.highest.position) return message.channel.send(`i can't give this role it's higher than mine`)

      if (role.position >= message.member.roles.highest.position) return message.channel.send(`you can't give this role as it's higher than you`)

      if (user.roles.cache.has(role.id)) {

        user.roles.remove(role.id).then(() => {
          return message.channel.send(`removed **${role.name}** from **${user.user.tag}** 👍`)
        }).catch(() => {
          return message.channel.send(`an error occured`)
        })
        
      } else {

        user.roles.add(role.id).then(() => {
          return message.channel.send(`added **${role.name}** to **${user.user.tag}** 👍`)
        }).catch(() => {
          return message.channel.send(`an error occured`)
        }) 
      }
    }
  }
}