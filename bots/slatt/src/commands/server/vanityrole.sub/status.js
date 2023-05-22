const Subcommand = require('../../Subcommand.js');
const db = require('quick.db')

module.exports = class role extends Subcommand {
  constructor(client) {
    super(client, {
      base: 'vanityrole',
      name: 'status',
      type: client.types.SERVER,
      usage: 'vanityrole status [vanity_url] or "none"',
      description: 'Update your servers vanityrole url',
    });
  }
  async run(message, args) {
    if (!args.length) return this.help(message)
    let check = await message.client.db.vanity_status.findOne({ where: { guildID: message.guild.id } })
    const status = args.join(' ')
    if (args[0] === 'none') {
      if (check !== null) {
        await message.client.db.vanity_status.destroy({ where: { guildID: message.guild.id } })
        return this.send_success(message, `Vanity role settings have been removed`)
      } else {
        return this.send_error(message, 1, `I could not find any vanityrole settings to remove`)
      }
    }
    if (check === null) {
      await message.client.db.vanity_status.create({
        guildID: message.guild.id,
        status: status
      })
    } else {
      await message.client.db.vanity_status.update({ status: status }, {
        where: { guildID: message.guild.id }
      })
    }
    return this.send_success(message, `Vanityrole status is now watching for **${status}**`)
  }
}