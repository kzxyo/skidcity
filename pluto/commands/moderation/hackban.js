const { MessageEmbed , Permissions} = require('discord.js');
const { prefix, color } = require("../../config.json");
const globaldataschema = require('../../database/global')

module.exports = {
  name: `hackban`,
  aliases: ['hban', 'hb'],

  run: async (client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) return message.channel.send(`this command requires \`ban members\` permission`)

        if(!message.guild.me.permissions.has(Permissions.FLAGS.BAN_MEMBERS)) return message.channel.send(`this command requires me to have \`ban members\` permission`)

    const embed = new MessageEmbed()
      .setColor(color)
      .setTitle(`${guildprefix}hackban`)
      .setDescription('ban user from guild even if they arent in the server')
      .addFields(
      { name: '**usage**', value: `${guildprefix}hackban [user]\n${guildprefix}hackban [user] [reason]`, inline: false },
      { name: '**aliases**', value: `hban, hb`, inline: false },
      )
      if (!args[0]) return message.channel.send({embeds: [embed] })

    const target = args[0];
    if (target.id == message.author.id) return message.channel.send({ embed: { color: "fe6464", description: `<:warning:1233044647601901650> ${message.author}: You cannot ban **yourself**` } })
    if (isNaN(target)) return message.channel.send({ embed: { color: "#efa23a", description: `<:warning:1233044647601901650> ${message.author}: You must to **specify** a valid user ID` } });

    const reason = args.splice(1, args.length).join(' ');

    message.guild.members.ban(target, { reason: reason.length < 1 ? 'No Reason Supplied' : reason });

    message.channel.send('👍')
  }
}