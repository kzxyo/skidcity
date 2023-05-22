const Discord = require('discord.js');
const pagination = require('discord.js-pagination');
const db = require('quick.db');
const { default_prefix } = require("../../config.json");
const { color } = require("../../config.json");

module.exports = {
  name: "help",

  run: async (client, message, args) => {
    let prefix = db.get(`prefix_${message.guild.id}`);
    if (prefix === null) { prefix = default_prefix; };
    if (message.author.bot) return;

    const page1 = new Discord.MessageEmbed()
      .setColor(color)
      .setThumbnail(client.user.displayAvatarURL({ format: "png", dynamic: true, size: 2048 }))
      .setAuthor(`${client.user.username} help`, client.user.displayAvatarURL())
      .setTitle('Launch Pad')
      .setDescription(`To get information on a command, invite ${client.user.username} to your server and run \`${prefix}[command]\`\nTo navigate through pages use the :arrow_left: or :arrow_right: arrow`)
      .addField(`**Want ${client.user.username} in your server?**`, `Invite ${client.user.username} [__here__](https://discord.com/api/oauth2/authorize?client_id=868297144480710756&permissions=8&scope=bot)`)
      .addField('**:newspaper: Latest News - July 23rd 2021**', 'lol four more like poor xd ! rofl.')

    const page2 = new Discord.MessageEmbed()
      .setColor(color)
      .setThumbnail(client.user.displayAvatarURL({ format: "png", dynamic: true, size: 2048 }))
      .setAuthor(`${client.user.username} help`, client.user.displayAvatarURL())
      .setTitle('**Configuration Commands**')
      .setDescription(`${prefix}altdentifier enable - enables altdentifer for the guild\n${prefix}altdentifier disable - disables altdentifier for the guild\n${prefix}autorole set - set the autorole for the guild\n${prefix}autorole clear - clear the original set autorole\n${prefix}modlogs channel - set your modlogs channel\n${prefix}modlogs clear - remove the current modlogs channel\n${prefix}prefix <prefix> - set command prefix for guild\n${prefix}welcome channel - set where to send welcome messages\n${prefix}welcome message - set the welcome message text\n${prefix}welcome test - test the welcome message\n${prefix}welcome variables - see all the welcome message variables`)

    const page3 = new Discord.MessageEmbed()
      .setColor(color)
      .setThumbnail(client.user.displayAvatarURL({ format: "png", dynamic: true, size: 2048 }))
      .setAuthor(`${client.user.username} help`, client.user.displayAvatarURL())
      .setTitle('**Fun Commands**')
      .setDescription(`${prefix}gnome - gnome the mentioned user\n${prefix}meme - sends a random meme off of reddit\n${prefix}randomnumber - get a random number\n${prefix}snipe - snipe the latest message that was deleted`)

    const page4 = new Discord.MessageEmbed()
      .setColor(color)
      .setThumbnail(client.user.displayAvatarURL({ format: "png", dynamic: true, size: 2048 }))
      .setAuthor(`${client.user.username} help`, client.user.displayAvatarURL())
      .setTitle('**Information Commands**')
      .setDescription(`${prefix}about - displays information about ${client.user.username}\n${prefix}help - displays this message embed\n${prefix}invite - sends an embed to invite ${client.user.username} w/ link\n${prefix}membercount - view the guilds member count\n${prefix}members - view members in a role\n${prefix}roleinfo - view information about a role\n${prefix}serverinfo - view information about the current guild\n${prefix}uptime - display ${client.user.username}'s uptime\n${prefix}userinfo - view information about a user/member`)

    const page5 = new Discord.MessageEmbed()
      .setColor(color)
      .setThumbnail(client.user.displayAvatarURL({ format: "png", dynamic: true, size: 2048 }))
      .setAuthor(`${client.user.username} help`, client.user.displayAvatarURL())
      .setTitle('**Last.fm Commands**')
      .setDescription(`${prefix}lastfm set - connect your Last.fm account\n${prefix}lastfm unlink - disconenct your Last.fm account\n${prefix}fm/np - shows your current song playing from Last.fm`)

    const page6 = new Discord.MessageEmbed()
      .setColor(color)
      .setThumbnail(client.user.displayAvatarURL({ format: "png", dynamic: true, size: 2048 }))
      .setAuthor(`${client.user.username} help`, client.user.displayAvatarURL())
      .setTitle('**Moderation Commands**')
      .setDescription(`${prefix}ban - bans the mentioned user from the guild\n${prefix}botclear - purge messages sent by bots\n${prefix}hackban - ban user from guild even if they arent in the server\n${prefix}kick - kicks the mentioned user from the guild\n${prefix}lockdown - lockdown a channel\n${prefix}mute - mutes the mentioned member in all channels\n${prefix}purge - deletes the specified amount of messages from the current channel\n${prefix}purgeuser - deletes the specified amount of messages from the mentioned user\n${prefix}rename - assigns the mentioned user a new nickname in the guild\n${prefix}role - adds role to member\n${prefix}rolecreate - creates a role with optional color\n${prefix}roleremove - removes role from a member\n${prefix}unban - unbans the mentioned user from the guild\n${prefix}unlock - unlock a channel\n${prefix}unmute - unmutes the mentioned member in all channels`)

    const page7 = new Discord.MessageEmbed()
      .setColor(color)
      .setThumbnail(client.user.displayAvatarURL({ format: "png", dynamic: true, size: 2048 }))
      .setAuthor(`${client.user.username} help`, client.user.displayAvatarURL())
      .setTitle('**Utility Commands**')
      .setDescription(`${prefix}afk - set an AFK status for when you are mentioned\n${prefix}appstore - search an app on the appstore\n${prefix}avatar - get avatar of a member or yourself \n${prefix}createembed - create your own embed\n${prefix}firstmessage - get a link for the first message in a channel\n${prefix}google - search the largest search engine on the internet (fixing)\n${prefix}guildbanner - returns guild banner\n${prefix}guildicon - returns guild icon\n${prefix}pin - pin any recent message by ID\n${prefix}poll - create poll\n${prefix}remind - get reminders for a duration set about whatever you choose\n${prefix}setbanner - set a new guild banner\n${prefix}seticon - set a new guild icon\n${prefix}setsplash - set a new guild splash\n${prefix}spotify - gives Spotify results for the current song playing\n${prefix}twitter - check a twitter account profile\n${prefix}unpin - unpin any recent message by ID\n${prefix}urban - gets the definition of word from urban dictionary\n${prefix}userbanner - get banner of a member or yourself`)

    const pages = [
      page1,
      page2,
      page3,
      page4,
      page5,
      page6,
      page7
    ]

    const emoji = ["⬅️", "➡️"]

    const timeout = '47000'

    pagination(message, pages, emoji, timeout)
  }
}
