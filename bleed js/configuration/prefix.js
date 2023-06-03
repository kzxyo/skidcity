const db = require("quick.db")
const { default_prefix } = require("../../config.json")
const { approve } = require('../../emojis.json')
const { warn } = require('../../emojis.json')

module.exports = {
  name: "prefix",

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_GUILD")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_guild\`` } });

    if (!args[0]) {
      return message.channel.send({ embed: { color: "#6495ED", description: `${message.author}: Please provide the prefix that you want to set` } })
    }

    if (args[1]) {
      return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: You cannot set the **prefix** to a **double argument**` } })
    }

    if (args[0].length > 3) {
      return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: Your **prefix** cannot be longer than **3 characters**!` } })
    }

    if (args.join("") === default_prefix) {
      db.delete(`prefix_${message.guild.id}`)
      return await message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: The guild's prefix has been reset to \`,\`` } })
    }

    db.set(`prefix_${message.guild.id}`, args[0])
    await message.channel.send({ embed: { color: "#a3eb7b", description: `${approve} ${message.author}: Replaced your current guild's prefix to \`${args[0]}\`` } })
  }
}