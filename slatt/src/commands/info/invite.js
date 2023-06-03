const Command = require('../Command.js');

module.exports = class InviteMeCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'invite',
      aliases: ['inv'],
      description: `my invite, use this to add me to your server`,
      subcommands: ['invite'],
      usage: 'inviteme',
      type: client.types.INFO
    });
  }
  async run(message) {    
      return this.send_info(message, `Slatt Bot invite: [invite](https://discord.com/api/oauth2/authorize?client_id=${message.client.user.id}&permissions=8&scope=bot)`)
  }
};
