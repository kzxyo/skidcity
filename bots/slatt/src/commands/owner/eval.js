const Command = require('../Command.js');
const {
  MessageEmbed
} = require('discord.js');

module.exports = class EvalCommand extends Command {
  constructor(client) {
    super(client, {
      name: 'eval',
      aliases: [`exec`],
      usage: `eval [code]`,
      description: 'Executes the provided code and shows output',
      type: client.types.OWNER,
      ownerOnly: true,
    });
  }
  async run(message, args) {
    const Discord = require('discord.js')
    let client = message.client
    const input = args.join(' ');
    if (!input) return this.send_error(message, 0, 'Please provide code to eval');
    const embed = new MessageEmbed()
    try {
      let output = eval(input);
      if (typeof output !== 'string') output = require('util').inspect(output, {
        depth: 0
      });

      embed
        .setDescription(`\`\`\`js\n${output.length > 1024 ? 'Too large to display.' : output}\`\`\``)
        .setColor('#66FF00');

    } catch (err) {
      embed
        .setDescription(`\`\`\`js\n${err.length > 1024 ? 'Too large to display.' : err}\`\`\``)
        .setColor('#FF0000');
    }

    message.channel.send({ embeds: [embed] });


  }
}