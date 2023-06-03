const Discord = require("discord.js");
const ms = require("ms");
const db = require("quick.db");
const { default_prefix } = require("../../config.json");
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
  name: "jail",

  run: async (client, message, args) => {
    if (!message.member.hasPermission("MANAGE_MESSAGES")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: You're **missing** permission: \`manage_messages\``}});
    if (!message.guild.me.hasPermission("MUTE_MEMBERS")) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: I'm **missing** permission: \`mute_members\``}});

    let prefix = db.get(`prefix_${message.guild.id}`);
    if (prefix === null) { prefix = default_prefix; };
    if (message.author.bot) return;

    const hackbanEmbed = new Discord.MessageEmbed()
      .setAuthor(message.author.username, message.author.avatarURL({
        dynamic: true
      }))
      .setTitle('Command: jail')
      .setDescription('Jails the mentioned user (timeout)')
      .addField('**Aliases**', 'N/A', true)
      .addField('**Parameters**', 'member, time, reason', true)
      .addField('**Information**', `${warn} Manage Messages`, true)
      .addField('**Usage**', '\`\`\`Syntax: jail (member) <duration> <reason>\nExample: jail four#0001 1h Being weird\`\`\`')
      .setFooter(`Module: moderation`)
      .setTimestamp()
      .setColor(color)
    if (!args[0]) return message.channel.send(hackbanEmbed)

    let user = message.guild.member(message.mentions.users.first() || message.guild.members.cache(args[0]));

    let log = await db.fetch(`logschannel_${message.guild.id}`)
    if (!log) return message.channel.send({ embed: { color: "efa23a", description: `${warn} ${message.author}: Modlogs channel was **not found** - set it using \`${prefix}modlogs channel (channel)\`` } })
    var mod = message.author
    var time = args[1]
    let rson = args.slice(2).join(' ')

    if (!user) return message.channel.send('You didn\'t mention a user')
    if (!time) return message.channel.send('Please write a time, Ex : 1s/1m/1h/1d/1w')
    if (!rson) return message.channel.send('You didn\'t say a reason!')


    const mute = message.guild.roles.cache.find(role => role.name === 'jailed')

    let mutetime = args[1]
    if (!mute) {
      let mute = await message.guild.roles.create({
        name: "jailed",
        color: "#818386",
        permissions: []
      })
      message.guild.channels.cache.filter(c => c.type === 'text').forEach(async (channel, id) => {
        await channel.overwritePermissions(mute, {
          VIEW_CHANNEL: false,
          READ_MESSAGE_HISTORY: false
        });
      });

    }


    await (user.addRole(mute.id));
    message.channel.send(``)
      .replace(`d`, " Day")
      .replace(`s`, " Second")
      .replace(`h`, " Hour")
      .replace(`m`, " Minute")
      .replace(`w`, " Week")
    message.channel.send(`${user} is now jailed for, **${mutetime}**`)
    db.set(`jailed_${message.guild.id + user.id}`, 'jailed')
    db.set(`jailtime_${message.mentions.users.first().id + message.guild.id}`, mutetime)

    const jailedembed = new Discord.MessageEmbed()
      .setTitle('Penal: Jail')
      .setThumbnail(user.avatarURL || user.defaultAvatarURL)
      .addField('Moderator', `${mod}`, true)
      .addField('Reason', `\`${rson}\``, true)
      .addField('User', `<@${user.id}>`, true)
      .addField('Time', `\`${mutetime}\``)
      .setColor("RANDOM")
    message.guild.channels.get(log).sendEmbed(jailedembed)

    setTimeout(function () {
      db.delete(`jailed_${message.guild.id + user.id}`)
      user.removeRole(mute.id)
      message.channel.send(`<@${user.id}> has been unjailed.`)
    }, ms(mutetime));

  }
}