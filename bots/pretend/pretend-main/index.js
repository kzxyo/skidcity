const { Client } = require("discord.js");
const Discord = require("discord.js");
const token = require('./config.json')
require("discord-reply");
require("discord-banner")();
const config = require("./config.json");
const googleIt = require('google-it')
const moment = require('moment');
const { MessageEmbed, version: djsversion } = require('discord.js');
const { Collection } = require('discord.js')
const client = new Discord.Client({
  allowedMentions: {
    restTimeOffset: 0,
    parse: ["roles", "users", "everyone"],
    repliedUser: false,
  },
  partials: ["MESSAGE", "CHANNEL", "REACTION"],
  intents: [
    Discord.Intents.FLAGS.GUILDS,
    Discord.Intents.FLAGS.GUILD_MEMBERS,
    Discord.Intents.FLAGS.GUILD_BANS,
    Discord.Intents.FLAGS.GUILD_EMOJIS_AND_STICKERS,
    Discord.Intents.FLAGS.GUILD_INTEGRATIONS,
    Discord.Intents.FLAGS.GUILD_WEBHOOKS,
    Discord.Intents.FLAGS.GUILD_INVITES,
    Discord.Intents.FLAGS.GUILD_VOICE_STATES,
    Discord.Intents.FLAGS.GUILD_PRESENCES,
    Discord.Intents.FLAGS.GUILD_MESSAGES,
    Discord.Intents.FLAGS.GUILD_MESSAGE_REACTIONS,
    //Discord.Intents.FLAGS.GUILD_MESSAGE_TYPING,
    Discord.Intents.FLAGS.DIRECT_MESSAGES,
    Discord.Intents.FLAGS.DIRECT_MESSAGE_REACTIONS,
    //Discord.Intents.FLAGS.DIRECT_MESSAGE_TYPING
  ],

  presence: {
    activities: [
      {
        name: `,help`,
        type: "PLAYING",
        url: "https://www.twitch.tv/ninja",
      },
    ],
    status: "dnd",
  },
});

const { get } = require("snekfetch");
const fetch = require('node-fetch')
const ms = require('ms')
const { MessageAttachment, MessageButton, MessageActionRow, WebhookClient, MessageSelectMenu } = require("discord.js");
const cooldown = new Set();
const cdtime = 5;
client.snipes = new Collection();
let south = "605366345902587921"
const akaneko = require("akaneko")
const translate = require("@iamtraction/google-translate");
const db = require("quick.db")
const talkedRecently = new Set();
const mongoose = require('mongoose')
const http = require("http");
const { banner_url } = require("discord-banner");
const { VoiceChannel } = require("discord.js");
const { id } = require("google-translate-api/languages");

client.on("ready", async (member) => {
let matatactu = new Discord.MessageEmbed()
.setColor("0CFF00")
.setDescription(`<:suffer_signal:985598537649778689> ${client.user.username} was reconnected to the host...`);


  console.log(`✅ bot is on`); 
}); 
/*


EVENTS



*/
client.on("message", async (message) => {
  let channel = db.fetch(`boostchannel_${message.guild.id}`);
  let text = db.fetch(`boostdesc_${message.guild.id}`)
  let img = db.fetch(`boostimage_${message.guild.id}`)
  let nail = db.fetch(`boostthumbnail_${message.guild.id}`)
  let col = db.fetch(`boostcolor_${message.guild.id}`)
  let tit = db.fetch(`boosttitle_${message.guild.id}`)
  let fot = db.fetch(`boostfooter_${message.guild.id}`)
  let titlol
  let tnail
  let mes
  let foter
  if(channel === null) return;
  if(text === null) return;
  if(!col) col = "RANDOM"
  if(tit) titlol = tit.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag)
  if(!tit) titlol = " "
  if(text) mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?mention`?/g, `${message.author}`).replace(/`?\?boostscount`?/g, `${message.guild.premiumSubscriptionCount}`);
  if(!fot) foter = " "
  if(fot) foter = fot.replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?boostscount`?/g, message.guild.premiumSubscriptionCount)
if(nail) tnail = nail.replace(/`?\?useravatar`?/g, message.author.displayAvatarURL({ dynamic: true })).replace(/`?\?serveravatar`?/g, message.guild.iconURL({ dynamic: true }))
if(!nail) tnail = " "
const embed = new Discord.MessageEmbed()
.setTitle(`${titlol}`)
.setDescription(`${mes}`)
.setColor(`${col}`)
.setImage(img)
.setThumbnail(tnail)
.setFooter(`${foter}`)
  if(message.type === 'USER_PREMIUM_GUILD_SUBSCRIPTION') {
  client.channels.cache.get(channel).send(message.author, {
embed: embed
})
  }
})

client.on("guildMemberAdd", async (member) => {
  let channel = db.get(`welcome_${member.guild.id}`);
        let text = db.get(`desc_${member.guild.id}`)
         let img = db.get(`image_${member.guild.id}`)
         let nail = db.get(`thumbnail_${member.guild.id}`)
         let me = db.get(`mention_${member.guild.id}`)
         let tit =  db.fetch(`title_${member.guild.id}`)
         let col = db.fetch(`color_${member.guild.id}`)
         let fot = db.fetch(`footer_${member.guild.id}`)
         let plaine = db.fetch(`welcometop_${member.guild.id}`)
         if (channel === null) {
          return;
        }
        let titlol 
        let mes
        let tnail
        let foter
        let isplaine
        if(!col) col = "RANDOM"
        if(!tit) titlol = " "
        if(tit) titlol = tit.replace(/`?\?user`?/g, member.user.username).replace(/`?\?server`?/g, member.guild.name).replace(/`?\?rank`?/g, member.guild.memberCount);
        if(!text) return 
        if(text) mes = text.replace(/`?\?user`?/g, member.user.username).replace(/`?\?server`?/g, member.guild.name).replace(/`?\?tag`?/g, member.user.tag).replace(/`?\?mention`?/g, `<@${member.user.id}>`).replace(/`?\?rank`?/g, member.guild.memberCount);
        if(!fot) foter = " "
        if(fot) foter = fot.replace(/`?\?user`?/g, member.user.username).replace(/`?\?server`?/g, member.guild.name).replace(/`?\?tag`?/g, member.user.tag).replace(/`?\?rank`?/g, member.guild.memberCount)
        if(!nail) tnail = " "
        if(nail) tnail = nail.replace(/`?\?useravatar`?/g, member.user.displayAvatarURL({ dynamic: true })).replace(/`?\?serveravatar`?/g, member.guild.iconURL({ dynamic: true }))
        if(!plaine) isplaine = " "
if(plaine) isplaine = plaine.replace(/`?\?user`?/g, member.user.username).replace(/`?\?server`?/g, member.guild.name).replace(/`?\?tag`?/g, member.user.tag).replace(/`?\?rank`?/g, member.guild.memberCount).replace(/`?\?mention`?/g, `<@${member.id}>`)
         const embed = new Discord.MessageEmbed()
         .setTitle(`${titlol}`)
         .setDescription(`${mes}`)
         .setColor(`${col}`)
         .setImage(img)
         .setThumbnail(tnail)
         .setFooter(`${foter}`)
         client.channels.cache.get(channel).send(isplaine, {
           embeds: [embed]
         })
})

client.on("guildMemberAdd", async (member) => {
let channel = db.fetch(`welcomeplainchannel_${member.guild.id}`)
let text = db.fetch(`welcomeplain_${member.guild.id}`)
if(channel === null) return;
if(text === null) return;
let mes = text.replace(/`?\?user`?/g, member.user.username).replace(/`?\?server`?/g, member.guild.name).replace(/`?\?tag`?/g, member.user.tag).replace(/`?\?mention`?/g, `<@${member.id}>`).replace(/`?\?rank`?/g, member.guild.memberCount)
client.channels.cache.get(channel).send(mes)
})

client.on("guildMemberAdd", (member) => {
  if(member.user.bot) return;
  let roleID = db.fetch(`autorole_${member.guild.id}`)
  if(!roleID) return;
  let role = member.guild.roles.cache.find(role => role.id == roleID);
  if(!role){
     console.log(console.error);
     return (false);
  }
  member.roles.add(role).catch(console.log(console.error))
})

client.on("guildMemberAdd", member => {
  if(!member.user.bot) return;
  let rolebot = db.fetch(`autorole_bots_${member.guild.id}`)
  if(!rolebot) return;
  let role = member.guild.roles.cache.find(role => role.id == rolebot)
  if(!role){
    console.log(console.error);
    return (false);
 }
 member.roles.add(role).catch(console.log(console.error))
})

client.on("guildMemberAdd", async (member) => {
  let channelID = db.fetch(`pingonjoin_${member.guild.id}`)
  if(!channelID) return;
  const channel = client.channels.cache.find(channel => channel.id === channelID)
  let msg = await channel.send(`${member}`)
        setTimeout(() => {
            msg.delete()
        }, 1000)
})

client.on("guildMemberAdd", (member) => {
  let mes = db.fetch(`joindm_${member.guild.id}`)
  if(!mes) return;
  let sending = mes.replace(/`?\?user`?/g, member.user.username).replace(/`?\?server`?/g, member.guild.name).replace(/`?\?tag`?/g, member.user.tag).replace(/`?\?mention`?/g, `<@${member.id}>`).replace(/`?\?rank`?/g, member.guild.memberCount)
  member.send(sending).catch(console.log(console.error))
})

client.on('messageDelete', (message) => {
  let snipes = client.snipes.get(message.channel.id) || [];
  if(snipes.lenght > 5) snipes = snipes.slice(0, 4);
  
  snipes.unshift({
      msg: message,
      image: message.attachments.first() ? message.attachments.first().proxyURL : null,
      time: Date.now(),
  })
  client.snipes.set(message.channel.id, snipes);
})

client.on('message', async(message) => {
  if(db.has(message.guild.id + message.content + 'autoresponder')) {
    if (message.author == client.user) return;
    if(message.author.bot) return;
  let mes = db.fetch(message.guild.id + message.content + 'autoresponder')
  message.channel.send(mes)
  }
})

/*


PING & UPTIME


*/
client.on("message", async(message)=>{
  if (!message.guild) return;
  if (message.author == client.user) return;
  if(message.author.bot) return;
  let prefix = db.fetch(`prefix_${message.guild.id}`)
  if(!prefix) prefix = ","
     if (message.content === `${prefix}ping`) {
      function doMagic8BallVoodoo() {
        var rand = [`**Elon Musk's spaceship**`, `**Putin's nuclear bomb**`, `**ap1q on tiktok**`, `**Mcdonalds's wifi**`, '**the chinese government**', '**your mom**', '**your dad**', '**some bitches**', '**north korea**', '**hot asian woman around your area**', '**webhost**', `**wintrs's luck**`];
    
        return rand[Math.floor(Math.random()*rand.length)];
    }
        let msg = await message.channel.send(`it took \`${Date.now() - message.createdTimestamp}ms\` to ping ${doMagic8BallVoodoo()}`)
            setTimeout(() => {
                msg.edit(`${msg} (edit: ${Math.round(message.client.ws.ping)}ms)`)
            }, 10)
  }
  if (message.content === `${prefix}uptime`) {
  const prettyMilliseconds = require("pretty-ms");
  const uptimeEmbed = new Discord.MessageEmbed()
.setAuthor(`${client.user.username}`, client.user.displayAvatarURL())
    .setDescription(` **:alarm_clock: ${client.user.username} has been up for ${prettyMilliseconds(client.uptime)}** `)
.setColor(`BLACK`)
.setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
                        dynamic: true
                    }))
.setTimestamp(Date.now());
message.reply({embeds: [uptimeEmbed]});
  }
  if(message.content.startsWith(`${prefix}prefix`) || message.content.startsWith(",setprefix")) {
    const missingperms = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions: \`manage_server\``)
  
          const missingargs = new Discord.MessageEmbed()
          .setTitle(`Missing arguments!`)
          .setColor(`FF0000`)
          .setDescription(`\`${prefix}setprefix [prefix]\`\nWe recommend to set the prefix to a symbol ex: !, -, #`)
          if(!message.member.permissions.has('MANAGE_GUILD')) return message.reply({embeds: [missingperms]});
          var args = message.content.substring().split(" ");
          let pref = args.slice(1).join(" ")
          if(!pref) return message.reply({embeds: [missingargs]});
          if(pref === ",") {
          db.delete(`prefix_${message.guild.id}`)
          const can = new Discord.MessageEmbed()
          .setColor(`0CFF00`)
          .setDescription(`<:approve:1006150867029864588>    set server prefix as ;`)
         message.reply({embeds: [can]});
          } else {
          db.set(`prefix_${message.guild.id}`, pref)
          const can = new Discord.MessageEmbed()
          .setColor(`0CFF00`)
          .setDescription(`<:approve:1006150867029864588>  >  set server prefix as ${pref}`)
         message.reply({embeds: [can]});
          }
  }
  /*



  HELP


  */

  if (message.content === `${prefix}help`) {
            const embed = new Discord.MessageEmbed()
                .setAuthor(message.author.username, message.author.avatarURL({ dynamic: true }))
                .setThumbnail('https://cdn.discordapp.com/avatars/1017895318664265728/3fd07ccbb416816c89b48706aa78b3f3.webp?size=1024')
              .addFields(
                { name: '**Help**', value: 'Use the dropdown menu below for the commands' },
                { name: '**Support**', value: `If you need further support make sure to join the **[Support Server](https://discord.gg/fancy)**` },
                { name: '**Invite**', value: `If you wanna invite ${client.user.username} to your server **[Click Here](https://discord.com/api/oauth2/authorize?client_id=${client.user.id}&permissions=8&scope=bot)**` },
              )
                .setFooter(`© ${client.user.username} | 106 commands`)
                .setColor(`BLACK`)
                .setTimestamp(Date.now());
    const row = new MessageActionRow()
      .addComponents(
        

        new MessageSelectMenu()
          .setCustomId('select')
          .setPlaceholder('Select category')
          .addOptions(
            {
              label: 'Information',
              description: 'Info Commands',
              value: 'two',
              emoji: '<:info:1009425742058237952> '
            },
            {
              label: 'Utility',
              description: 'Utility Commands',
              value: 'three',
              emoji: '<:icons_link:1014291269415096330>  '

            },
            {
              label: 'Moderation',
              description: 'Moderation Commands',
              value: 'four',
              emoji: '<:icons_verified:1014299559020732507>   '

            },
            {
              label: 'Configuration',
              description: 'Configuration Commands',
              value: 'five',
              emoji: '<:icons_settings:1014300181803573288>   '

            },
            {
              label: 'Welcome setup',
              description: 'Welcome Commands',
              value: 'six',
              emoji: '<:icons_Person:1014300348183236749>   '

            },
            {
              label: 'Boost message setup',
              description: 'Boost Commands',
              value: 'seven',
              emoji: '<:boosterbadge:1014300731722960946>   '

            },
            {
              label: 'Fun',
              description: 'Fun Commands',
              value: 'eight',
              emoji: '<:icons_bulb:976526713209106452>   '

            },
            {
              label: 'Roleplay',
              description: 'Roleplay commands',
              value: 'nine',
              emoji: '<:icons_Person:1014300348183236749>   '

            },

          ),
      );
    await message.reply({ embeds: [embed], components: [row] })

    const embed1 = new Discord.MessageEmbed()
      .setAuthor(`Module: Information`, message.author.displayAvatarURL({dynamic:true}))
      .setDescription(`\`ping, uptime, support, invite, guildcount, prefix, owners\``)
      .setFooter(`© raid | 106 commands`)
      .setColor('BLACK')
      
    const embed2 = new Discord.MessageEmbed()
      .setAuthor(`Module: Utility`, message.author.displayAvatarURL({ dynamic: true }))
      .setDescription(`\`avatar, serverinfo, membercount, boostscount, guildicon, guildbanner, userinfo, embed, poll, firstmessage, afk, downloademoji, cryptocurrency, emojilist, serverstats, getbotinvite\``)
      .setFooter(`© raid | 106 commands`)
      .setColor('BLACK')

    const embed3 = new Discord.MessageEmbed()
      .setAuthor(`Module: Moderation`, message.author.displayAvatarURL({ dynamic: true }))
      .setDescription(`\`ban, unban, kick, purge, lock, unlock, role\``)
      .setFooter(`© raid | 106 commands`)
      .setColor('BLACK')


    const embed4 = new Discord.MessageEmbed()
      .setAuthor(`Module: Configuration`, message.author.displayAvatarURL({ dynamic: true }))
      .setDescription(`\`setguildicon, setguildname, setguildbanner, setnickname, setbotnickname, emoji, imgaddemoji, addmultiple, setautorole, deleteautorole, autorole list, setpingonjoin, deletepingonjoin,
pingonjoin list, setjoindm, deletejoindm, joindm message, setautoresponder, deleteautoresponder\``)
      .setFooter(`© raid | 106 commands`)
      .setColor('BLACK')

    const embed6 = new Discord.MessageEmbed()
      .setAuthor(`Module: Welcome setup`, message.author.displayAvatarURL({ dynamic: true }))
      .setDescription(`\`setwelcomechannel, setwelcomecolor, setwelcometitle, setwelcomedescription, setwelcomethumbnail, setwelcomeimage, setwelcomefooter, setwelcomemessage, testwelcome, welcome variables, deletewelcome, help welcome, setplainwelcome, setwelcomeplainchannel, testplainwelcome, deleteplainwelcome\``)
      .setFooter(`© raid | 106 commands`)
      .setColor('BLACK')
      
    const embed7 = new Discord.MessageEmbed()
      .setAuthor(`Module: Boost message setup`, message.author.displayAvatarURL({ dynamic: true }))
      .setDescription(`\`setboostchannel, setboosttitle, setboostdescription, setboostcolor, setboostthumbnail, setboostimage, setboostfooter, testboost, help boost, boost variables\``)
      .setFooter(`© raid | 106 commands`)
      .setColor('BLACK')

    const embed8 = new Discord.MessageEmbed()
      .setAuthor(`Module: Fun`, message.author.displayAvatarURL({ dynamic: true }))
      .setDescription(`\`gay, ship, 8ball, cat, dog, say, iq, meme, truth, dare, advice, hot, translate, search, tts, ben\``)
      .setFooter(`© raid | 106 commands`)
      .setColor('BLACK')

    const embed9 = new Discord.MessageEmbed()
      .setAuthor(`Module: Roleplay`, message.author.displayAvatarURL({ dynamic: true }))
      .setDescription(`\`hug, kiss, pat, cuddle, slap, kill, cry, eat, dance, laugh\``)
      .setFooter(`© raid | 106 commands`)
      .setColor('BLACK')
    const collector = message.channel.createMessageComponentCollector({
      componentType: "SELECT_MENU"
    })
    collector.on("collect", async (collected) => {
      const value = collected.values[0]

      if (value === "two"){
        collected.reply({embeds: [embed1], ephemeral:true})
      }
      if (value === "three") {
          collected.reply({ embeds: [embed2], ephemeral: true })
        }
      if (value === "four") {
            collected.reply({ embeds: [embed3], ephemeral: true })
          }
      if (value === "five") {
              collected.reply({ embeds: [embed4], ephemeral: true })
            }
      if (value === "six") {
                collected.reply({ embeds: [embed6], ephemeral: true })
              }
      if (value === "seven") {
                  collected.reply({ embeds: [embed7], ephemeral: true })
                }
      if (value === "eight") {
        collected.reply({ embeds: [embed8], ephemeral: true })
      }
      if (value === "nine") {
        collected.reply({ embeds: [embed9], ephemeral: true })
      }
              })
            }
          
       
  if (message.content === `${prefix}owners`) {
            const embed = new Discord.MessageEmbed()
                .setAuthor(message.author.username, message.author.avatarURL({ dynamic: true }))
                
                .setTitle('Owners')

              .setDescription(`**[wintrs#2000](https://discord.com/users/605366345902587921) - Bot developer**
              **[terrify#0001](https://discord.com/users/968269401767940207) - Bot helper**`)
                .setFooter(`${client.user.username}`)
                .setColor(`BLACK`)
                .setTimestamp(Date.now());
                
               message.reply({embeds: [embed]})
  
        }
        if(message.content === `${prefix}help nsfw` || message.content === `${prefix}nsfw help`) {
        if (!message.channel.nsfw) {
          const nonnsfw = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604> >   ${message.author}: You're not allowed to use **nsfw** commands here`)
          message.reply({embeds: [nonnsfw]})
        } else {
         const nsfwhelp = new Discord.MessageEmbed()
         .setTitle(`NSFW Commands`)
         .setColor(`BLACK`)
         .setDescription(`Type \`${prefix}nsfw [command]\` for results
        
\`ass\`, \`bdsm\`, \`blowjob\`, \`cum\`, \`blowjob\`, \`doujin\`, \`feet\`, \`femdom\`, \`foxgirl\`, \`gifs\`, \`glasses\`, \`hentai\`, \`netorare\`, \`maid\`, \`masturbation\`, \`orgy\`, \`panties\`, \`pussy\`, \`school\`, \`succubus\`, \`tentacles\`, \`thighs\`, \`uglyBastard\`, \`uniform\`, \`yuri\`, \`zettaiRyouiki\`, \`cum\`, \`boobs\`, \`spank\`, \`lesbian\`, \`4k\``)
          .setFooter(`© ${client.user.username} | 31 nsfw commands`)
                .setTimestamp(Date.now());
         message.reply({embeds: [nsfwhelp]})
        }
      }
        if(message.content === `${prefix}help ping`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}ping`)
          .setColor(`BLACK`)
          .setDescription(`Shows bots ping`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({embeds: [helpavatar]})
        }
        if(message.content === `${prefix}help setprefix`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}setprefix [prefix]`)
          .setColor(`BLACK`)
          .setDescription(`Sets server's prefix for the bot\nWe recommend to set the prefix to a symbol ex: !, -, #\nYou can also change the server's prefix by using the default prefix of the bot: \`;\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({embeds: [helpavatar]})
        }
        if(message.content === `${prefix}help uptime`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}uptime`)
          .setColor(`BLACK`)
          .setDescription(`Shows how long the bot has been up for`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar]})
        }
        if(message.content === `${prefix}help serverstats`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}serverstats`)
          .setColor(`BLACK`)
          .setDescription(`Shows how many members are online and how many members are offline in the server!`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help role`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}role+/- [user id / user mention / user id] [role name]`)
          .setColor(`BLACK`)
          .setDescription(`Adds a role to an user or removes a role from an user
**Example:**

${prefix}role+ @wintrs#2000 staff or ${prefix}role+ 605366345902587921 staff
(adds role to user)

${prefix}role- @wintrs#2000 special or ${prefix}role- 605366345902587921 special
(removes role from user)

Aliases: \`roleadd\`, \`roleremove\`, \`rolermv\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}helpsetguildname`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}setguildname [name]`)
          .setColor(`BLACK`)
          .setDescription(`Changes server's name\nAliases: \`setservername\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help setautorole`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}setautorole humans [role mention / role id] (sets autorole for humans)\n${prefix}setautorole bots [role mention / role id] (sets autorole for bots)`)
          .setColor(`BLACK`)
          .setDescription(`Configures auto role to the server`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help deleteautorole`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}deleteautorole [role mention / role id]`)
          .setColor(`BLACK`)
          .setDescription(`Removes a role from autorole configuration in your server\nAliases: \`delautorole`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}helpautorole list`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}autorole list`)
          .setColor(`BLACK`)
          .setDescription(`Shows all roles that are given automatically`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help setpingonjoin`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}setpingonjoin [channel mention / channel id]`)
          .setColor(`BLACK`)
          .setDescription(`Pings new members in the specific channel when they join the server`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help deletepingonjoin`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}deletepingonjoin [channel mention / channel id]`)
          .setColor(`BLACK`)
          .setDescription(`Removes a channel from pinging new members\nAliases: \`delpingonjoin`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help pingonjoin list`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}autorole list`)
          .setColor(`BLACK`)
          .setDescription(`Shows all channels where new members are pinged`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help setautoresponder`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}setautoresponder [trigger] [response]`)
          .setColor(`BLACK`)
          .setDescription(`Sets a message for the bot to respond at. Note that triggers that contain spaces might break your setup`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help deleteautoresponder`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}deleteautoresponder [trigger]`)
          .setColor(`BLACK`)
          .setDescription(`Deletes a message for the bot to respond at\nAliases: \`delautoresponder\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help setjoindm`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}setjoindm [message]`)
          .setColor(`BLACK`)
          .setDescription(`Sets a message to be sent to the new members that are joining the server`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help deletejoindm`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}deletejoindm`)
          .setColor(`BLACK`)
          .setDescription(`Removes the join dm message\nAliases: \`deljoindm`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help joindm message`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}autorole list`)
          .setColor(`BLACK`)
          .setDescription(`Shows the message that it will be sent to members in dm's`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help getbotinvite`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}getbotinvite [bot id]`)
          .setColor(`BLACK`)
          .setDescription(`Gets bot invite link with administrator permission`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help setguildicon`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}setguildicon [image link]`)
          .setColor(`BLACK`)
          .setDescription(`Changes server's icon\nAliases: \`setservericon\`, \`setserveravatar\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help setguildbanner`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}setguildbanner [image link]`)
          .setColor(`BLACK`)
          .setDescription(`Changes server's bannner (server needs to have atleast 7 boosts to use this command)\nAliases: \`setserverbanner\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help addemoji`) {
          let helpemoji = new Discord.MessageEmbed()
          .setTitle(`${prefix}addemoji [emoji] [emoji name (optional)]`)
          .setColor(`BLACK`)
          .setDescription(`Adds an external emoji to the server`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpemoji] })
        }
        if(message.content === `${prefix}help addmultiple`) {
          let helpemoji = new Discord.MessageEmbed()
          .setTitle(`${prefix}addmultiple [emojis]`)
          .setColor(`BLACK`)
          .setDescription(`Adds multiple emojis to the server`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpemoji] })
        }
        if(message.content === `${prefix}help emojilist`) {
          let helpemoji = new Discord.MessageEmbed()
          .setTitle(`${prefix}emojilist`)
          .setColor(`BLACK`)
          .setDescription(`Shows all emojis from the server!`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpemoji] })
        }
        if(message.content === `${prefix}help downloademoji`) {
          let helpemoji = new Discord.MessageEmbed()
          .setTitle(`${prefix}downloademoji [emoji]`)
          .setColor(`BLACK`)
          .setDescription(`Sends the png or gif file so you can download any emoji you want!`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpemoji] })
        }
        if(message.content === `${prefix}help imgaddemoji`) {
          let helpemoji = new Discord.MessageEmbed()
          .setTitle(`${prefix}imgaddemoji [image link] [emoji name]`)
          .setColor(`BLACK`)
          .setDescription(`Adds an image as emoji to the server`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpemoji] })
        }
        if(message.content === `${prefix}help cryptocurrency`) {
          let helpemoji = new Discord.MessageEmbed()
          .setTitle(`${prefix}cryptocurrency [crypto coin]`)
          .setColor(`BLACK`)
          .setDescription(`Shows value of a crypto coin!`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpemoji] })
        }
        if(message.content === `${prefix}help ben`) {
          let helpemoji = new Discord.MessageEmbed()
          .setTitle(`${prefix}ben [question]`)
          .setColor(`BLACK`)
          .setDescription(`Answers to your question with yes, no, uhh or hohoho by sending a talking ben video saying those things`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpemoji] })
        }
        if(message.content === `${prefix}help support`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}support`)
          .setColor(`BLACK`)
          .setDescription(`Sends an invite to the support server`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help invite`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}invite`)
          .setColor(`BLACK`)
          .setDescription(`Sends an invite link of the bot`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help search`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}search [message]`)
          .setColor(`BLACK`)
          .setDescription(`Shows results of the message you typed!`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help guildcount`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}guildcount`)
          .setColor(`BLACK`)
          .setDescription(`Shows the number of the servers the bot is in`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help afk`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}afk [reason (optional)]`)
          .setColor(`BLACK`)
          .setDescription(`Let the members know that you are afk!`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help botinfo`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}botinfo`)
          .setColor(`BLACK`)
          .setDescription(`Shows you informations about the bot`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help snipe`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}snipe`)
          .setColor(`BLACK`)
          .setDescription(`Shows the last deleted message from the channel\n\nAliases: \`s\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help advice`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}advice`)
          .setColor(`BLACK`)
          .setDescription(`Sends an advice`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help startgiveaway`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}startgiveaway [duration] [winners] [#channel] [prize]`)
          .setColor(`BLACK`)
          .setDescription(`Sets a giveaway!
Example: \`${prefix}startgiveaway 24h 3w #giveaways Free Discord Nitro\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help avatar`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}avatar [user mention (optional)]`)
          .setColor(`BLACK`)
          .setDescription(`Shows mentioned member's avatar
          Aliases: \`av\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help translate`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}translate [language] [word]`)
          .setColor(`BLACK`)
          .setDescription(`Auto detects the language of the word you typed and translates it in the language you want to!

supported languages: af, sq, am, ar, hy, az, eu, be, bn, bs, bg, ca, ceb, ny, zh-CN, zh-TW, co, hr, cs, da, nl, en, eo, et, tl, fi, fr, fy, gl, ka, de, el, gu, ht, ha, haw, he, iw, hi, hmn, hu, is, ig, id, ga, it, ja, jw, kn, kk, km, ko, ku, ky, lo, la, lv, lt, lb, mk, mg, ms, ml, mt, mi, mr, mn, my, ne, no, ps, fa, pl, pt, pa, ro, ru, sm, gd, sr, st, sn, sd, si, sk, sl, so, es, su, sw, sv, tg, ta, te, th, tr, uk, ur, uz, vi, cy, xh, yi, yo, zu`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help setnickname`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}setnickname [user mention / user id] [nickname]`)
          .setColor(`BLACK`)
          .setDescription(`Sets a nickname to an user
Aliases: \`setnick\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help setbotnickname`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}setbotnickname [nickname]`)
          .setColor(`BLACK`)
          .setDescription(`Sets a nickname to the bot
Aliases: \`setbotnick\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help serverinfo`) {
          let helpsi = new Discord.MessageEmbed()
          .setTitle(`${prefix}serverinfo`)
          .setColor(`BLACK`)
          .setDescription (`Shows information about the server
          Aliases: \`server\`, \`si\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
        .setTimestamp()
          message.reply({ embeds: [helpsi] })
        }
        if(message.content === `${prefix}help membercount`) {
          let helpmc = new Discord.MessageEmbed()
          .setTitle(`${prefix}membercount`)
          .setColor(`BLACK`)
          .setDescription (`Shows the number of members and bots the server has
          Aliases: \`mc\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
        .setTimestamp()
          message.reply({ embeds: [helpmc] })
        }
        if(message.content === `${prefix}help boostscount`) {
          let helpmc = new Discord.MessageEmbed()
          .setTitle(`${prefix}boostscount`)
          .setColor(`BLACK`)
          .setDescription (`Shows the number of boosts the server has
          Aliases: \`bc\`, \`boostcount\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
        .setTimestamp()
          message.reply({ embeds: [helpmc] })
        }
        if(message.content  === `${prefix}help userinfo`) {
            let helpuser = new Discord.MessageEmbed()
            .setTitle(`${prefix}userinfo [user mention (optional)]`)
            .setColor(`BLACK`)
            .setDescription (`Shows the information about the mentioned user
            Aliases: \`ui\`, \`whois\``)
            .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
              dynamic: true
          }))
          .setTimestamp()
          message.reply({ embeds: [helpuser] })
        }
        if(message.content === `${prefix}help guildicon`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}guildicon`)
          .setColor(`BLACK`)
          .setDescription(`Shows the server's icon\nAliases: \`servericon\`, \`serveravatar\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help guildbanner`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}guildbanner`)
          .setColor(`BLACK`)
          .setDescription(`Shows the server's banner (only png version sadly)\nAliases: \`serverbanner\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help embed`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}embed [message]`)
          .setColor(`BLACK`)
          .setDescription(`Sends an embed message of your choice (MANAGE_SERVER permission to the user requiFF0000 to use this command)`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help poll`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}poll [message]`)
          .setColor(`BLACK`)
          .setDescription(`Sends a poll message (MANAGE_SERVER permission to the user requiFF0000 to use this command)`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help banner`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}banner [user mention (optional)]`)
          .setColor(`BLACK`)
          .setDescription(`Shows the user's banner`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help ban`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}ban [user mention / user id] [reason (optional)]`)
          .setColor(`BLACK`)
          .setDescription(`Bans the mentioned user (BAN_MEMBERS permission requieFF0000 to the user to ban members)`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help unban`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}unban [user id]`)
          .setColor(`BLACK`)
          .setDescription(`Unbans the user (BAN_MEMBERS permission requieFF0000 to the user to unban members)`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help kick`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}kick [user mention / user id] [reason (optional)]`)
          .setColor(`BLACK`)
          .setDescription(`Kicks the mentioned user (BAN_MEMBERS or KICK_MEMBERS permission requieFF0000 to the user to ban members)`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help purge`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}purge [number of messages]`)
          .setColor(`BLACK`)
          .setDescription(`Deletes an ammount of messages (MANAGE_SERVER permission requieFF0000 to the user to ban members)`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help lock`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}lock`)
          .setColor(`BLACK`)
          .setDescription(`Locks the channel`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help unlock`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}lock`)
          .setColor(`BLACK`)
          .setDescription(`Unlocks the channel`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help gay`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}gay [user mention (optional)]`)
          .setColor(`BLACK`)
          .setDescription(`Gay rates the mentioned user`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help hot`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}hot [user mention (optional)]`)
          .setColor(`BLACK`)
          .setDescription(`Hot rates the mentioned user`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help ship`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}ship [user mention]`)
          .setColor(`BLACK`)
          .setDescription(`Ship rates you with the mentioned user`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help 8ball`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}8ball [question]`)
          .setColor(`BLACK`)
          .setDescription(`Answers to your question with \`yes or no\` responses`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help cat`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}cat`)
          .setColor(`BLACK`)
          .setDescription(`Shows a random cat picture`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help dog`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}dog`)
          .setColor(`BLACK`)
          .setDescription(`Shows a random dog picture`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help say`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}say`)
          .setColor(`BLACK`)
          .setDescription(`Say a message in an embed`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help dm`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}dm [user mention/id] [message]`)
          .setColor(`BLACK`)
          .setDescription(`Directly messages an user (don't use it maliciously please...)`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help iq`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}iq [user mention (optional)]`)
          .setColor(`BLACK`)
          .setDescription(`Shows your iq`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help meme`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}meme`)
          .setColor(`BLACK`)
          .setDescription(`Shows a random meme`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help hug`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}hug [user mention]`)
          .setColor(`BLACK`)
          .setDescription(`Hugs the mentioned user`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help kiss`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}kiss [user mention]`)
          .setColor(`BLACK`)
          .setDescription(`Kisses the mentioned user`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help pat`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}pat [user mention]`)
          .setColor(`BLACK`)
          .setDescription(`Pats the mentioned user`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help cuddle`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}cuddle [user mention]`)
          .setColor(`BLACK`)
          .setDescription(`Cuddles the mentioned user`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help slap`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}slap [user mention]`)
          .setColor(`BLACK`)
          .setDescription(`Slaps the mentioned user`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help kill`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}kill [user mention]`)
          .setColor(`BLACK`)
          .setDescription(`Kills the mentioned user`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help cry`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}cry`)
          .setColor(`BLACK`)
          .setDescription(`Shows crying animation`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help eat`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}eat`)
          .setColor(`BLACK`)
          .setDescription(`Shows eating animation`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help firstmessage`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}firstmessage`)
          .setColor(`BLACK`)
          .setDescription(`Shows the first message sent in the server
          Aliases: \`firstmsg\``)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help dance`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}dance`)
          .setColor(`BLACK`)
          .setDescription(`Shows dancing animation`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help laugh`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}laugh`)
          .setColor(`BLACK`)
          .setDescription(`Shows laughing animation`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help truth`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}truth`)
          .setColor(`BLACK`)
          .setDescription(`Shows a truth question`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
        if(message.content === `${prefix}help tts`) {
          let helptts = new Discord.MessageEmbed()
          .setTitle(`${prefix}tts [message]`)
          .setColor(`BLACK`)
          .setDescription(`Sends your message as text to speech`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helptts] })
        }
        if(message.content === `${prefix}help dare`) {
          let helpavatar = new Discord.MessageEmbed()
          .setTitle(`${prefix}dare`)
          .setColor(`BLACK`)
          .setDescription(`Shows a dare`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
            dynamic: true
        }))
          .setTimestamp()
          message.reply({ embeds: [helpavatar] })
        }
          if (message.content.includes("@here") || message.content.includes("@everyone")) return false;
if (message.mentions.has(client.user.id)) {
  const prefixebed = new Discord.MessageEmbed().setDescription(`:wave: Prefix: ${prefix}`)
  message.reply({embeds: [prefixebed]})
} 
/* 


GROWTH


*/
if (message.content === `${prefix}invite`|| message.content === `${prefix}support`) {

  const embed = new Discord.MessageEmbed()
    .setTitle(' ')
    .setColor("BLACK")
    .setDescription(`
>  **Type** \`${prefix}help\` **for more commands. Join the support server [Support](https://discord.gg/kN4JKK2nCM)**`)
              .setFooter(
                  `requested by ${message.author.username}`,
                  message.author.displayAvatarURL({
                      dynamic: true
                  })
              )
          .setTimestamp(Date.now())
    .setColor('BLACK')
const row = new MessageActionRow().addComponents(
  new MessageButton()
    .setLabel("Invite Link")
    .setURL(`https://discord.com/api/oauth2/authorize?client_id=${client.user.id}&permissions=8&scope=bot`)
    .setStyle('LINK'),
)
message.reply({ embeds: [embed], components: [row] })
}
  /* 


  FUN


  */
  if(message.content.startsWith(`${prefix}gay`)) {
    let gay = Math.floor(Math.random() * 101);
    if(message.mentions.users.size){
            let member=message.mentions.users.first() || message.guild.members.cache.get(params[1])
        if(member) {
          const emb = new Discord.MessageEmbed()
          .setTitle(`Howgay`)
          .setColor(`BLACK`)
          .setDescription(`**${member.username} is __${gay}%__ gay🏳️‍🌈**`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
                        dynamic: true
                    }))
                    .setTimestamp()
          message.reply({ embeds: [emb] })
        } 
         
  } 
  }
   if (message.content === `${prefix}gay`) {
    let gay = Math.floor(Math.random() * 101);
    const embed = new Discord.MessageEmbed()
          .setTitle(`Howgay`)
          .setColor(`BLACK`)
          .setDescription(`**${message.author.username} is __${gay}%__ gay🏳️‍🌈**`)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
                        dynamic: true
                    }))
                    .setTimestamp()
     message.reply({ embeds: [embed] })
                  }
                  if (message.content === `${prefix}iq`) {
                    let iq = Math.floor(Math.random() * 201);
                    const embed = new Discord.MessageEmbed()
                          .setTitle(`iq test`)
                          .setColor(`BLACK`)
                          .setDescription(`**${message.author.username} has __${iq}__ iq**`)
                          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
                                        dynamic: true
                                    }))
                                    .setTimestamp()
                    message.reply({ embeds: [embed] })
                                  }
                                  if(message.content.startsWith(`${prefix}iq`)) {
                                    let iq = Math.floor(Math.random() * 201);
                                    if(message.mentions.users.size){
                                            let member=message.mentions.users.first() || message.guild.members.cache.get(params[1])
                                        if(member) {
                                          const emb = new Discord.MessageEmbed()
                                          .setTitle(`iq test`)
                                          .setColor(`BLACK`)
                                          .setDescription(`**${member.username} has __${iq}__ iq**`)
                                          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
                                                        dynamic: true
                                                    }))
                                                    .setTimestamp()
                                          message.reply({ embeds: [emb] })
                                        }   
                                  } 
                                  }
                                  if (message.content === `${prefix}hot`) {
                                    let hot = Math.floor(Math.random() * 101);
                                    const embed = new Discord.MessageEmbed()
                                          .setTitle(`Howhot`)
                                          .setColor(`BLACK`)
                                          .setDescription(`**${message.author.username} is __${hot}%__ hot**`)
                                          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
                                                        dynamic: true
                                                    }))
                                                    .setTimestamp()
                                    message.reply({ embeds: [embed] })
                                                  }
                                                  if(message.content.startsWith(`${prefix}hot`)) {
                                                    let hot = Math.floor(Math.random() * 101);
                                                    if(message.mentions.users.size){
                                                            let member=message.mentions.users.first() || message.guild.members.cache.get(params[1])
                                                        if(member) {
                                                          const emb = new Discord.MessageEmbed()
                                                            .setTitle(`Howhot`)
                                                          .setColor(`BLACK`)
                                                          .setDescription(`**${member.username} is __${hot}%__ hot**`)
                                                          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
                                                                        dynamic: true
                                                                    }))
                                                                    .setTimestamp()
                                                          message.reply({ embeds: [emb] })
                                                        }   
                                                  } 
                                                  }
                                  if(message.content === `${prefix}advice`) {
                                    function advicesforu() {
                                      var rand = [
                                       "Your life is your responsibility.",
                                       "The way someone treats you is a reflection of how they feel about themselves.",
                                       "Life is all about managing expectations—most of all your own.",
                                       "When you know better, do better.",
                                       "Your word is your bond.",
                                       "Work hard. Stay humble.",
                                       "Just keep going. No matter what.",
                                       "Release the idea that things could’ve been any other way.",
                                       "Listen more than you speak.",
                                       "Do what you’re afraid to do.",
                                       "Be kind. Always.",
                                       "Don't get addicted to discord =]]",
                                       "It's not worth spending money on this app",
                                       "Get some girls xd",
                                       "Your school grades won't 100% determine your future",
                                       "Focus on your hobbies. These will help u acomplish everything in life"]
                                   return rand[Math.floor(Math.random()*rand.length)];
                                    }
                                    const response = new Discord.MessageEmbed()
                                    .setTitle(`Advice`)
                                    .setColor(`BLACK`)
                                    .setThumbnail(`https://files.schudio.com/alder-community-high-school/images/news/advice.jpg`)
                                    .setDescription(`**` + advicesforu() + `**`)
                                    message.reply({ embeds: [response] });
                                  }            
           if(message.content === `${prefix}truth`) {
             function truthIsAlwaysPainful() {
               var rand = [
                "When was the last time you lied?",
                "When was the last time you cried?",
                "What's your biggest fear?",
                "What's your biggest fantasy?",
                "Do you have any fetishes?",
                "What's something you're glad your mum doesn't know about you?",
                "Have you ever cheated on someone?",
                "What's the worst thing you've ever done?",
                "What's a secret you've never told anyone?",
                "Do you have a hidden talent?",
                "Who was your first celebrity crush?",
                "What are your thoughts on polyamory?",
                "What's the worst intimate experience you've ever had?",
                "Have you ever cheated in an exam?",
                "What's the most drunk you've ever been?",
                "Have you ever broken the law?",
                "What's the most embarrassing thing you've ever done?",
                "What's your biggest insecurity?",
                "What's the biggest mistake you've ever made?",
                "What's the most disgusting thing you've ever done?",
                "Who would you like to kiss in this room?",
                "What's the worst thing anyone's ever done to you?",
                "Have you ever had a run in with the law?",
                "What's your worst habit?",
                "What's the worst thing you've ever said to anyone?",
                "Have you ever peed in the shower?",
                "What's the strangest dream you've had?",
                "Have you ever been caught doing something you shouldn't have?",
                "What's the worst date you've been on?",
                "What's your biggest regret?",
                "What's the biggest misconception about you?",
                "Where's the weirdest place you've had sex?",
                "Why did your last relationship break down?",
                "Have you ever lied to get out of a bad date?",
                "What's the most trouble you've been in?" ]
            return rand[Math.floor(Math.random()*rand.length)];
             }
             const response = new Discord.MessageEmbed()
             .setTitle(`Truth`)
             .setColor(`BLACK`)
             .setDescription(`**` + truthIsAlwaysPainful() + `**`)
             message.reply({ embeds: [response] });
           }
           if(message.content === `${prefix}dare`) {
            function dareIsMorePainful() {
              var rand = [
                "Show the most embarrassing photo on your phone",
                "Show the last five people you texted and what the messages said",
                "Let the rest of the group DM someone from your Instagram account",
                "Say something dirty to the first person that dm's you",
                "Spam out the first word that comes to your mind",
                "Add a random person then tell them that you are their lost sibling",
                "Send a sext to the last person in your dms",
                "Show off your orgasm face",
                "Empty out your wallet/purse and show everyone what's inside",
                "Moan like an egirl on vc",
                "Say two honest things about everyone else in the group",
                "Say i love you to your favourite girl/boy from the server",
                "Try and make the group laugh as quickly as possible",
                "Tell everyone an embarrassing story about yourself",
                "Send a picture with the last dm you sent",
                "Post the oldest selfie on your phone on Instagram Stories",
                "Leave a random server",
                "Tell the saddest story you know" ]
           return rand[Math.floor(Math.random()*rand.length)];
            }
            const response = new Discord.MessageEmbed()
            .setTitle(`Dare`)
            .setColor(`BLACK`)
            .setDescription(`**` + dareIsMorePainful() + `**`)
             message.reply({ embeds: [response] });
          }
 if(message.content.startsWith(`${prefix}8ball`)){
    if(message.content === (`${prefix}8ball`)) {
      const missingargs = new Discord.MessageEmbed()
      .setTitle(`Missing arguments`)
      .setDescription(`\`${prefix}8ball [question]\``)
      .setColor(`BLACK`)
      message.reply({ embeds: [missingargs] })
    }
    args = message.content.split(" ").slice(1);
    var argresult = args.join(' ');
              if(argresult) {
                function doMagic8BallVoodoo() {
    var rand = ['**Yes**', '**No**', '**definitely yes**', '**Of course not**', '**Maybe**', '**Never**', '**Yes, dummy**', '**No wtf**'];

    return rand[Math.floor(Math.random()*rand.length)];
}
 message.reply('> ' + doMagic8BallVoodoo());
              }
  }
  if(message.content.startsWith(`${prefix}ben`)){
    const missingperms = new Discord.MessageEmbed()
    .setColor(`FFF300`)
    .setDescription(`<:warn:1006150861195587604>    ${client.user} is missing permsission \`attach_files\``)
    if(message.content === (`${prefix}ben`)) return message.reply("Please ask a question")
    if (!message.guild.me.permissions.has('ATTACH_FILES')) return message.reply({ embeds: [missingperms] })
    args = message.content.split(" ").slice(1);
    var argresult = args.join(' ');
              if(argresult) {
                function BenSystem() {
    var rand = ['benyes.mp4', 'benno.mp4', 'benuhh.mp4', 'benhoho.mp4'];

    return rand[Math.floor(Math.random()*rand.length)];
}
let file = new MessageAttachment(BenSystem())
 message.reply(file);
              }
  }
  /*


  PROFILE


  */



  if(message.content.startsWith(`${prefix}av`) || message.content.startsWith(`${prefix}avatar`)){
   if(message.mentions.users.size){
            let member=message.mentions.users.first() ||  message.guild.members.cache.get(args[1])
        if(member){
            const emb=new Discord.MessageEmbed().setImage(member.displayAvatarURL(({
                       size: 1024,
                        dynamic: true
                    })))
                    .setAuthor(member.tag, member.displayAvatarURL({
                        dynamic: true
                    }))
                    .setColor(`BLACK`)
          message.reply({ embeds: [emb] })
            
        }
        else{
            message.reply("Sorry no one found with that name")

        }
        }else{
            const emb=new Discord.MessageEmbed().setImage(message.author.displayAvatarURL(({
              size: 1024,
                        dynamic: true
                    }))).setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
                    .setColor(`BLACK`)
     message.reply({ embeds: [emb] })
        }
}
if(message.content === `${prefix}about`){
  let days = Math.floor(client.uptime / 86400000);
  let hours = Math.floor(client.uptime / 3600000) % 24;
  let minutes = Math.floor(client.uptime / 60000) % 60;
  let seconds = Math.floor(client.uptime / 1000) % 60;

  let UptimeDays = days
  if (UptimeDays) {
    UptimeDays = `${days} days, `;
  } else {
    UptimeDays = ''
  }

  let UptimeHours = hours
  if (UptimeHours) {
    UptimeHours = `${hours} hours, `;
  } else {
    UptimeHours = ''
  }

  let UptimeMinutes = minutes
  if (UptimeMinutes) {
    UptimeMinutes = `${minutes} minutes, `;
  } else {
    UptimeMinutes = ''
  }

  let UptimeSeconds = seconds
  if (UptimeSeconds) {
    UptimeSeconds = `${seconds} seconds`;
  } else {
    UptimeSeconds = ''
  }




  const embed = new Discord.MessageEmbed()
    .setColor('BLACK')
    .setAuthor(`${client.user.username}`, client.user.displayAvatarURL())
    .setDescription(`**<:icons_owner:1018868665321525258>  Developer: -->** **[wintrs#2000](https://discord.com/users/605366345902587921)** \n**<:Bug:1009380172895629332> Memory:** \`${(process.memoryUsage().rss / 1024 / 1024).toFixed(2)}\`**MB**\n**<:icons_settings:1006151454505046056> Cmd Count: --> ** \`106\``)
    .addField('**<:icons_user:1018869289870176357>  Members:**', `${client.guilds.cache.reduce((current, guild) => current + guild.memberCount, 0).toLocaleString()}`, true)
    .addField('**<:suffer_channel:1006495811665940510> Channels:**', `${client.channels.cache.size.toLocaleString()} Total`, true)
    .addField('**<:icons_settings:1006151454505046056>  Guilds: **', `${client.guilds.cache.size.toLocaleString()} `, true)
    .addField('**<:upvote:1012289701379584040>  Uptime: **', `${UptimeDays}${UptimeHours}${UptimeMinutes}${UptimeSeconds}`, true)

    .setFooter(`Requested by ${message.author.tag}`)
    .setTimestamp() 
  message.reply({ embeds: [embed] })
}
if(message.content === `${prefix}dog`) {
    const prevmsg = message
    const fetchEmbed = new Discord.MessageEmbed()
      .setColor('BLACK')
      .setTitle(':dog: Woof! Let me find you a doggo!')
      .setDescription("This shouldn't take long...")
  message.reply({ embeds: [fetchEmbed] }).then(async (msg) => {
      const { message } = await fetch('https://dog.ceo/api/breeds/image/random').then(response => response.json());
      console.log(message)
      const doneEmbed = new Discord.MessageEmbed()
      .setColor('BLACK')
      .setTitle(':dog: Woof! Found one!')
      .setImage(message)
      msg.delete();
    prevmsg.channel.send({ embeds: [doneEmbed] });
    })
};
if(message.content.toLowerCase().startsWith(`${prefix}getbotinvite`)) {
  const missingargs = new Discord.MessageEmbed()
  .setColor(`FF0000`)
  .setDescription(`\`${prefix}getbotinvite [bot id]`)
  args = message.content.split(" ").slice(1);
  let botid = args.slice(0).join(' ');
  if (!botid) return message.reply({ embeds: [missingargs] })
  const botinv = new Discord.MessageEmbed()
  .setColor(`BLACK`)
  .setDescription(`[Invite the bot](https://discord.com/api/oauth2/authorize?client_id=${botid}&permissions=8&scope=bot%20applications.commands)`)
  message.reply({ embeds: [botinv] })
}
  if (message.content.startsWith(`${prefix}cat`)) {
    const prevmsg = message
    const fetchEmbed = new Discord.MessageEmbed()
      .setColor('BLACK')
      .setTitle(':cat: Meow! Let me find you a kitty!')
      .setDescription("This shouldn't take long...")
    message.reply({ embeds: [fetchEmbed] }).then(async (msg) => { 
      const { file } = await fetch('https://aws.random.cat/meow').then(response => response.json());
      console.log(message)
      const doneEmbed = new Discord.MessageEmbed()
      .setColor('BLACK')
      .setTitle(':cat: Meow! Found one!')
      .setImage(file)
      msg.delete();
        prevmsg.channel.send({ embeds: [doneEmbed] });
    })
                     };
    if(message.content.startsWith(`${prefix}purge`)) {
      if (!message.member.permissions.has(['MANAGE_MESSAGES']) || !message.guild.me.permissions.has('MANAGE_MESSAGES')) {
            const missingperms = new Discord.MessageEmbed()
            .setColor(`FFF300`)
                .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_messages\``)
        message.reply({ embeds: [missingperms] })
      } else {
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}purge [number of messages]\``)

        const bignumber = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription("<:warn:1006150861195587604>   **Please select a number** ***between*** **5000 and 1**")

        const limitation = new Discord.MessageEmbed()
        .setColor(`BLACK`)
          .setDescription(`<:deny:1016352259111669841> Due to Discord Limitations, I cannot delete messages older than 14 days`)
         args = message.content.split(" ").slice(1);
      var amount = parseInt(args[0])
      
        if (!amount) return message.reply({ embeds: [missingargs] })
        if (amount >= 5000 || amount < 1) return message.channel.send({ embeds: [bignumber] })

        message.channel.bulkDelete(amount + 1).catch(err => {
          message.channel.send({ embeds: [limitation] }) })

        const embed = new Discord.MessageEmbed().setDescription(`<:approve:1006150867029864588>  Deleted \`${amount}\` messages`).setColor('0CFF00')
        let msg = await message.channel.send({embeds: [embed]})
        setTimeout(() => {
            msg.delete()
        }, 2000)
      }
    }
    if(message.content.startsWith(`${prefix}ship`)) {
    let ship = Math.floor(Math.random() * 101);
    let text1 = "*You two are definitely soulmates <3*";
    let text2 = "*A relationship could work*";
    let text3 = "*Don't be more than bestfriends*";
    let text4 = "*Just stay friends*";
    let text5 = "*You guys hate each other*";
    let finaltext = "text"
    if(ship === 100) {
      finaltext = text1;
    } else if (ship >= 75 && ship < 100) {
      finaltext = text2;
    } else if (ship >= 50 && ship < 75) {
      finaltext = text3
    } else if (ship >= 25 && ship < 50) {
      finaltext = text4
    } else {
      finaltext = text5
    }
    if(message.mentions.users.size){
            let member=message.mentions.members.first();
        if(member) {
          const emb = new Discord.MessageEmbed()
          .setColor(`BLACK`)
          .setThumbnail(`https://bestanimations.com/uploads/gifs/1220963497spinning-transparent-heart-animation61.gif`)
          .setDescription(`**
                ${message.author.username} ❤️ ${message.mentions.users.first().username}**
                            \`${ship}%\`
              ${finaltext}
                `)
          .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
                        dynamic: true
                    }))
                    .setTimestamp()
          message.reply({ embeds: [emb] })
        } 
         else{
            message.reply("Sorry no one found with that name")

        }
  } else {
     const missingargs = new Discord.MessageEmbed()
      .setTitle(`Missing arguments`)
      .setDescription(`\`${prefix}ship [user mention]\``)
      .setColor(`BLACK`)
      message.reply({ embeds: [missingargs] })
  }
  }
  if(message.content.startsWith(`${prefix}cryptocurrency`)) {
    const isEmptyObject = (obj) => Object.keys(obj).length === 0;
    args = message.content.split(" ").slice(1);
    let cc = args.slice(0).join(' ');
    if (!cc) {
      const noArgs = new Discord.MessageEmbed()
        .setTitle('Missing arguments')
        .setColor('FF0000')
        .setDescription(
          `\`${prefix}cryptocurrency [crypto coin]\``
        )
        .setTimestamp(new Date().getTime());
      message.reply({ embeds: [noArgs] });
    }
    const response = await fetch(
      `https://api.coingecko.com/api/v3/simple/price?ids=${cc}&vs_currencies=usd%2Ceur%2Cgbp`
    );
    const data = await response.json();

    if (isEmptyObject(data) && cc) {
      let empty = new Discord.MessageEmbed()
      .setColor(`FF0000`)
      .setDescription(`<:deny:999025481183662110> No returned data from the API<:joeyidk:938785951868661791> Are you sure "${cc}" is a valid id?`)
      return message.channel.send({ embeds: [empty] })
    }
    let usdprice = data[cc].usd;
    let europrice = data[cc].eur;
    let gbpprice = data[cc].gbp;
    const embed = new Discord.MessageEmbed()
      .setTitle(`**Current price of ${cc}:**`)
      .setDescription('This data might be inaccurate.')
      .setColor('BLACK')
      .setTimestamp(new Date().getTime())
      .addField('**USD:**', usdprice, true)
      .addField('**EURO:**', europrice, true)
      .addField('**GBP:**', gbpprice, true)
      .setFooter(`Requested by ${message.author.username}`, message.author.displayAvatarURL({
        dynamic:true
      }))
    message.reply({ embeds: [embed] });
  }
  if(message.content.startsWith(`${prefix}say`)) {
    args = message.content.split(" ").slice(1);
    var argresult = args.join(' ');
    if(argresult) {
      message.delete()
      const say = new Discord.MessageEmbed() 
      .setColor(`BLACK`)
      .setDescription(`**${message.author.username} said... ** 
      ${argresult}`)
      .setTimestamp()
      message.channel.send({ embeds: [say] })
    } else {
      const missingargs = new Discord.MessageEmbed()
      .setTitle(`Missing arguments`)
      .setColor(`FF0000`)
      .setDescription(`\`${prefix}say [message]\``)
      message.reply({ embeds: [missingargs] })
    }
  }
  message.mentions.users.forEach((user) => {
    if(message.author.bot) return false;
    
      if (
       message.content.includes('@here') ||
       message.content.includes('@everyone')
      )
       return false;
      if (db.has(user.id + message.guild.id + '.afk')) {
        let reasontosend = db.fetch(user.id + message.guild.id + '.messageafk')
        if(!reasontosend) reasontosend = "AFK"
        let time = db.fetch(user.id + message.guild.id + '.afktime')
      let warning = new Discord.MessageEmbed()
      .setColor(`FFF300`)
      .setDescription(`<:warn:1006150861195587604>    ${user} is currently AFK: ${reasontosend} - **${moment(time).fromNow()}**`)
        message.reply({ embeds: [warning] })
      }
     });
  if (db.has(message.author.id + message.guild.id + '.afk')) {
    let time = db.fetch(message.author.id + message.guild.id + '.afktime')
    let come = new Discord.MessageEmbed()
    .setColor(`BLACK`)
    .setDescription(`👋 Welcome back ${message.author} I removed your AFK. You were away **${moment(time).fromNow()}**`)
    message.channel.send({ embeds: [come] });
    message.member.setNickname(`${message.author.username}`).catch(error => { 
      console.log(`unable to change nickname`) 
    });
    db.delete(message.author.id + message.guild.id + '.afk');
    db.delete(message.author.id + message.guild.id + '.messageafk');
    db.delete(message.author.id + message.guild.id + '.afktime');
   }
   if (message.content.startsWith(`${prefix}afk`)) {
    args = message.content.split(" ").slice(1);
    const reason = args.join(' ')
    message.member.setNickname(`[AFK] ${message.author.username}`).catch(error => { 
      message.channel.send(`unable to change nickname, is my role above all members? 🤔`) 
    });
    db.set(message.author.id + message.guild.id + '.afk', 'true');
    db.set(message.author.id + message.guild.id + '.messageafk', reason)
    db.set(message.author.id + message.guild.id + '.afktime', Date.now())
    let afk = new Discord.MessageEmbed()
    .setColor(`0CFF00`)
    .setDescription(`<:approve:1006150867029864588>   ${message.author} is now AFK! ${reason}`)
     message.channel.send({ embeds: [afk] })
   }
if(message.content === `${prefix}guildicon` || message.content === `${prefix}servericon` || message.content === `${prefix}serveravatar`) {
  const icon = new Discord.MessageEmbed()
  .setTitle(`${message.guild.name}'s avatar`)
  .setColor(`BLACK`)
  .setImage(message.guild.iconURL({
    size: 1024,
                        dynamic: true
                    })) 
                    .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
                        dynamic: true
                    }))
                    .setTimestamp()
                    message.reply({embeds: [icon]})
}
if(message.content === `${prefix}guildbanner` || message.content === `${prefix}serverbanner`) {
  const icon = new Discord.MessageEmbed()
  .setTitle(`${message.guild.name}'s banner`)
  .setColor(`BLACK`)
  .setImage(message.guild.bannerURL({
    size: 1024,
                        dynamic: true
                    })) 
                    .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
                        dynamic: true
                    }))
                    .setTimestamp()
  message.reply({ embeds: [icon] })
}
if(message.content === `${prefix}boostscount` || message.content === `${prefix}boostcount` || message.content === `${prefix}bc`) {
  const boostcounter = new Discord.MessageEmbed()
  .setTitle(`Boosts`)
  .setColor(`BLACK`)
  .setDescription(`**${message.guild.premiumSubscriptionCount}**`)
  message.reply({embeds: [boostcounter]})
}
if(message.content === `${prefix}membercount` || message.content === `${prefix}mc`){
  const members = message.guild.members.cache;
  const mc = new Discord.MessageEmbed()
    .setTitle(`${message.guild.name}'s member count`)
    .setDescription(`>>> **This server has** \`${message.guild.memberCount}\` **members!**

    **Humans:** \`${members.filter(member => !member.user.bot).size}\`
    **Bots:** \`${members.filter(member => member.user.bot).size}\``)
    .setColor(`BLACK`)
    .setThumbnail(message.guild.iconURL({ dynamic: true }))
    .setFooter(`requested by ${message.author.username}`, message.author.displayAvatarURL({
                        dynamic: true
                    }))
                    .setTimestamp()
                    message.reply({embeds: [mc]})
}
  if(message.content.startsWith(`${prefix}whois`) || message.content.startsWith(`${prefix}userinfo`) || message.content.startsWith(`${prefix}ui`)) {
    const flags = {
      DISCORD_EMPLOYEE: "Discord Employee",
      DISCORD_PARTNER: "Discord Partner",
      BUGHUNTER_LEVEL_1: "Bug Hunter (Level 1)",
      BUGHUNTER_LEVEL_2: "Bug Hunter (Level 2)",
      HYPESQUAD_EVENTS: "HypeSquad Events",
      HOUSE_BRAVERY: "House of Bravery",
      HOUSE_BRILLIANCE: "House of Brilliance",
      HOUSE_BALANCE: "House of Balance",
      EARLY_SUPPORTER: "Early Supporter",
      TEAM_USER: "Team User",
      SYSTEM: "System",
      VERIFIED_BOT: "Verified Bot",
      VERIFIED_DEVELOPER: "Verified Bot Developer",
    };

    const user =
      message.mentions.users.first() ||
      message.author;
    const member = message.guild.members.cache.get(user.id);

    const userFlags = member.user.flags.toArray();

    const userinfoembed = new Discord.MessageEmbed()
      .setAuthor(
        `${user.tag}`,
        user.displayAvatarURL({ dynamic: true })
      )
      .setThumbnail(`${user.displayAvatarURL({ dynamic: true })}`)
      .setColor("BLACK")
      .addFields(
        {
          name: "<:icons_settings:1006151454505046056>   Username:",
          value: `> ${user.tag}`,
        },
        {
          name: "<:suffer_id:993724825015160882>  User Id:",
          value: `> ${user.id}`,
        },
        {
          name: "<:suffer_channel:1006495811665940510> Discriminator:",
          value: `> #${user.discriminator}`,
        },
        {
          name: "<:icons_verified:999050643828379829> Flags:",
          value: `> ${userFlags.length
              ? userFlags.map((flag) => flags[flag]).join(", ")
              : "None"
            }`,
        },
        {
          name: "<:icons_user:1018869289870176357>   Account Created At:",
          value: `> ${member.user.createdAt}`,
        },
        {
          name: "<:icons_user:1018869289870176357>   Joined Guild At:",
          value: `> ${member.joinedAt}`,
        }
      )
      .setFooter(`${user.id}`)
    .setTimestamp()
    message.reply({ embeds: [userinfoembed]});            
                }
                  if(message.content === `${prefix}firstmessage` || message.content === `${prefix}firstmsg`) {
                    const fetchMessages = await message.channel.messages.fetch({
                      after: 1,
                      limit: 1,
                    });
                    const msg = fetchMessages.first();
                
                    message.reply({ embeds: [
                      new MessageEmbed()
                        .setTitle(`First Messsage in ${message.channel.name}`)
                        .setURL(msg.url)
                        .setColor(`BLACK`)
                        .setThumbnail(msg.author.displayAvatarURL({ dynamic: true }))
                        .setDescription("Content: " + `\`${msg.content}\``)
                        .addField("Author", `\`${msg.author.tag}\``, true)
                        .addField('Message ID', `\`${msg.id}\``, true)
                        .addField('Created At', `\`${message.createdAt.toLocaleDateString()}\``, true)
                  ]});
                  }
                  /*


                  TENOR API


                  */
                  if(message.content.startsWith(`${prefix}pat`)) {
                    if (!message.mentions.users.first()) {
                    let missingargs = new Discord.MessageEmbed()
                    .setTitle(`Missing arguments!`)
                    .setColor(`BLACK`)
                    .setDescription(`\`${prefix}pat [user]\``)
              return message.reply({embeds: [missingargs]});
                    }
          let keywords = 'anime pat';
          let url = `https://g.tenor.com/v1/search?q=${keywords}&key=${process.env.TENORKEY}&contentfilter=low`;
          let response = await fetch(url);
          let json = await response.json();
          const index = Math.floor(Math.random() * json.results.length);
          const embed = new Discord.MessageEmbed()
          .setColor('BLACK')
          .setTitle(`*Aww how cute, ${message.author.username} pats ${message.mentions.users.first().username}!*`,)
          .setImage(json.results[index].media[0].gif.url)
           message.channel.send({embeds: [embed]})
          }
                  if(message.content.startsWith(`${prefix}kiss`)) {
                    if (!message.mentions.users.first()) {
                    let missingargs = new Discord.MessageEmbed()
                    .setTitle(`Missing arguments!`)
                    .setColor(`BLACK`)
                    .setDescription(`\`${prefix}kiss [user]\``)
              return message.reply({embeds: [missingargs]});
                    }
          let keywords = 'anime kiss';
          let url = `https://g.tenor.com/v1/search?q=${keywords}&key=${process.env.TENORKEY}&contentfilter=low`;
          let response = await fetch(url);
          let json = await response.json();
          const index = Math.floor(Math.random() * json.results.length);
          const embed = new Discord.MessageEmbed()
          .setColor('BLACK')
          .setTitle(`*Aww how cute, ${message.author.username} kissed ${message.mentions.users.first().username}!*`,)
          .setImage(json.results[index].media[0].gif.url)
                    message.channel.send({ embeds: [embed] })
          }
          if(message.content === (`${prefix}cry`)) {
            let keywords = 'anime cry';
            let url = `https://g.tenor.com/v1/search?q=${keywords}&key=${process.env.TENORKEY}&contentfilter=low`;
            let response = await fetch(url);
            let json = await response.json();
            const index = Math.floor(Math.random() * json.results.length);
            const embed = new Discord.MessageEmbed()
            .setColor('BLACK')
            .setTitle(`${message.author.username} cries`,)
            .setImage(json.results[index].media[0].gif.url)
            message.channel.send({ embeds: [embed] })
            }
            if(message.content === (`${prefix}dance`)) {
              let keywords = 'anime dance';
              let url = `https://g.tenor.com/v1/search?q=${keywords}&key=${process.env.TENORKEY}&contentfilter=low`;
              let response = await fetch(url);
              let json = await response.json();
              const index = Math.floor(Math.random() * json.results.length);
              const embed = new Discord.MessageEmbed()
              .setColor('BLACK')
              .setTitle(`${message.author.username} dances`,)
              .setImage(json.results[index].media[0].gif.url)
              message.channel.send({ embeds: [embed] })
              }
              if(message.content === (`${prefix}laugh`)) {
                let keywords = 'laugh';
                let url = `https://g.tenor.com/v1/search?q=${keywords}&key=${process.env.TENORKEY}&contentfilter=low`;
                let response = await fetch(url);
                let json = await response.json();
                const index = Math.floor(Math.random() * json.results.length);
                const embed = new Discord.MessageEmbed()
                .setColor('BLACK')
                .setTitle(`${message.author.username} laughs`,)
                .setImage(json.results[index].media[0].gif.url)
                message.channel.send({ embeds: [embed] })
                }
          if(message.content === (`${prefix}eat`)) {
  let keywords = 'anime eat';
  let url = `https://g.tenor.com/v1/search?q=${keywords}&key=${process.env.TENORKEY}&contentfilter=low`;
  let response = await fetch(url);
  let json = await response.json();
  const index = Math.floor(Math.random() * json.results.length);
  const embed = new Discord.MessageEmbed()
  .setColor('BLACK')
  .setTitle(`${message.author.username} eats`,)
  .setImage(json.results[index].media[0].gif.url)
            message.channel.send({ embeds: [embed] })
  }
                  if(message.content.startsWith(`${prefix}kill`)) {
                    let user = message.mentions.users.first()
                  if (!message.mentions.users.first()) {
                  let missingargs = new Discord.MessageEmbed()
                  .setTitle(`Missing arguments!`)
                  .setColor(`BLACK`)
                  .setDescription(`\`${prefix}kill [user]\``)
                    return message.reply({ embeds: [missingargs] });
                  }
                  if(user.id === message.author.id) return message.reply("Are you depressed or something? <:Cat_Sad:1006717285311983756>")
                  if(user.bot === true) return message.reply("*Robots are too cool to destroy!* says the Discord Team")
        let keywords = 'anime kill';
        let url = `https://g.tenor.com/v1/search?q=${keywords}&key=${process.env.TENORKEY}&contentfilter=low`;
        let response = await fetch(url);
        let json = await response.json();
        const index = Math.floor(Math.random() * json.results.length);
        const embed = new Discord.MessageEmbed()
        .setColor('BLACK')
        .setTitle(`${message.author.username} killed ${message.mentions.users.first().username}`)
        .setImage(json.results[index].media[0].gif.url)
                    message.channel.send({ embeds: [embed] })
        }
        if(message.content.startsWith(`${prefix}slap`)) {
          if (!message.mentions.users.first()) {
          let missingargs = new Discord.MessageEmbed()
          .setTitle(`Missing arguments!`)
          .setColor(`BLACK`)
          .setDescription(`\`${prefix}slap [user]\``)
            return message.reply({ embeds: [missingargs] });
          }
let keywords = 'anime slap';
let url = `https://g.tenor.com/v1/search?q=${keywords}&key=${process.env.TENORKEY}&contentfilter=low`;
let response = await fetch(url);
let json = await response.json();
const index = Math.floor(Math.random() * json.results.length);
const embed = new Discord.MessageEmbed()
.setColor('BLACK')
.setTitle(` ${message.author.username} slapped ${message.mentions.users.first().username}`)
.setImage(json.results[index].media[0].gif.url)
          message.channel.send({ embeds: [embed] })
}
if(message.content.startsWith(`${prefix}hug`)) {
  if (!message.mentions.users.first()) {
  let missingargs = new Discord.MessageEmbed()
  .setTitle(`Missing arguments!`)
  .setColor(`BLACK`)
  .setDescription(`\`${prefix}hug [user]\``)
return message.reply({embeds: [missingargs]});
  }
let keywords = 'anime hug';
let url = `https://g.tenor.com/v1/search?q=${keywords}&key=${process.env.TENORKEY}&contentfilter=low`;
let response = await fetch(url);
let json = await response.json();
const index = Math.floor(Math.random() * json.results.length);
const embed = new Discord.MessageEmbed()
.setColor('BLACK')
.setTitle(`*Aww how cute, ${message.author.username} gave ${message.mentions.users.first().username} a hug!*`,)
.setImage(json.results[index].media[0].gif.url)
message.channel.send({embeds: [embed]})
}
if(message.content.startsWith(`${prefix}cuddle`)) {
  if (!message.mentions.users.first()) {
  let missingargs = new Discord.MessageEmbed()
  .setTitle(`Missing arguments!`)
  .setColor(`BLACK`)
  .setDescription(`\`${prefix}cuddle [user]\``)
return message.reply({embeds: [missingargs]});
  }
let keywords = 'anime cuddle';
let url = `https://g.tenor.com/v1/search?q=${keywords}&key=${process.env.TENORKEY}&contentfilter=low`;
let response = await fetch(url);
let json = await response.json();
const index = Math.floor(Math.random() * json.results.length);
const embed = new Discord.MessageEmbed()
.setColor('BLACK')
.setTitle(`*Aww how cute, ${message.author.username} cuddles ${message.mentions.users.first().username}!*`,)
.setImage(json.results[index].media[0].gif.url)
message.channel.send({embeds: [embed]})
}
if(message.content === (`${prefix}meme`)) {
  let keywords = 'meme';
  let url = `https://g.tenor.com/v1/search?q=${keywords}&key=${process.env.TENORKEY}&contentfilter=low`;
  let response = await fetch(url);
  let json = await response.json();
  const index = Math.floor(Math.random() * json.results.length);
  const embed = new Discord.MessageEmbed()
  .setColor('BLACK')
  .setTitle(`${message.author.username} here is a meme`,)
  .setImage(json.results[index].media[0].gif.url)
   message.channel.send({embeds: [embed]})
  }
  /*


  DM, SNIPE, EMBED, DONATE


  */
                  if(message.content.startsWith(`${prefix}dm`)) {
                    var params = message.content.substring().split(" ");
                    params[0] = params[0].toLowerCase();
                    let member = message.mentions.users.first() || message.guild.members.cache.get(params[1])
                    let missingargs = new Discord.MessageEmbed()
                    .setTitle(`Missing arguments!`)
                    .setColor(`FF0000`)
                    .setDescription(`\`${prefix}dm [user] [message]\``)
                    .setTimestamp()
                    if(!params[1]) return message.reply({embeds: [missingargs]});
                    message.delete();
                    let msg = params.slice(2).join(' ');
                    if(!msg) return message.reply("> **Type the command again but this time enter a message**");
                    if(msg.includes('discord.gg') || msg.includes('http://') || msg.includes('https://') || msg.includes('www.') || msg.includes('./gg')) return message.reply(`**No links in dm's!**`)
                    let msgEmbed = new Discord.MessageEmbed().setColor("BLACK").setFooter(`Sent by ${message.author.tag}`).setDescription(msg)
                    member.send({embeds : [msgEmbed]})
                    .catch(error => { 
                    message.reply(`**User DMs are closed**`) 
                  })

            }

 
if(message.content.startsWith(`${prefix}embed`)) {
      if (! message.member.permissions.has(['ADMINISTRATOR'] || ['MANAGE_SERVER']))  {
      const missingperms = new Discord.MessageEmbed()
      .setColor(`FFF300`)
      .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
      message.reply({embeds: [missingperms]});
} else {
    args = message.content.split(" ").slice(1);
              var argresult = args.join(' ');
              if(argresult) {
                const result = new Discord.MessageEmbed()
                .setColor(`BLACK`)
                .setDescription(`${argresult}`)
                .setTimestamp()
                let msg = message.channel.send({embeds: [result]})
                message.delete()
              }
            }
            if(!argresult && message.member.permissions.has(['ADMINISTRATOR'] || ['MANAGE_SERVER'])) {
              const missingargs = new Discord.MessageEmbed()
              .setTitle(`Missing arguments`)
              .setDescription(`\`${prefix}embed [message]\``)
              .setColor(`FF0000`)
              message.reply({embeds: [missingargs]});
            }
            } 
            /*


            LOCK UNLOCK


            */
            if(message.content === `${prefix}lock`) {
              if(! message.member.permissions.has('MANAGE_ROLES')) {
                const missingperms = new Discord.MessageEmbed()
                .setColor(`FFF300`)
                .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_roles\``)
                message.reply({ embeds: [missingperms]});
              } else {
                message.channel.permissionOverwrites.create(message.channel.guild.roles.everyone, { SEND_MESSAGES: false });
                const success = new Discord.MessageEmbed()
                .setColor(`0CFF00`)
                .setDescription(`<:approve:1006150867029864588>   ${message.channel} locked succesfully!`)
                message.reply({embeds: [success]});
              }
              if (!message.guild.me.permissions.has('MANAGE_ROLES')) { 
                const perms = new Discord.MessageEmbed()
                .setColor(`FFF300`)
                .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`manage_roles\``)
                message.reply({embeds: [perms]});
               }
            }
            if(message.content === `${prefix}unlock`) {
              if(! message.member.permissions.has('MANAGE_ROLES')) {
                const missingperms = new Discord.MessageEmbed()
                .setColor(`FFF300`)
                .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_roles\``)
                message.reply({ embeds: [missingperms]});
              } else {
                message.channel.permissionOverwrites.create(message.channel.guild.roles.everyone, { SEND_MESSAGES: true });
                const success = new Discord.MessageEmbed()
                .setColor(`0CFF00`)
                .setDescription(`<:approve:1006150867029864588>   ${message.channel} unlocked succesfully!`)
                message.reply({embeds: [success]});
              }
              if (!message.guild.me.permissions.has('MANAGE_ROLES')) { 
                const perms = new Discord.MessageEmbed()
                .setColor(`FFF300`)
                .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`manage_roles\``)
                message.reply({embeds: [perms]});
               }
            }
            /*


            CUSTOMIZE SERVER


            */
            if(message.content.startsWith(`${prefix}setguildicon`) || message.content.startsWith(`${prefix}setservericon`) || message.content.startsWith(`${prefix}setserveravatar`)) {
              if (!message.guild.me.permissions.has('MANAGE_GUILD')) { 
                const perms = new Discord.MessageEmbed()
                .setColor(`FFF300`)
                .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`manage_server\``)
                message.reply({embeds: [perms]});
               }
              if (! message.member.permissions.has(['ADMINISTRATOR'])) {
                const missingperms = new Discord.MessageEmbed()
                .setColor(`FFF300`)
                .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`administrator\``)
                message.reply({embeds: [missingperms]});
            } else {
               args = message.content.split(" ").slice(1);
                         var argresult = args.join(' ');
                         if(argresult) {
                          let changed = new Discord.MessageEmbed()
                          .setColor(`0CFF00`)
                          .setDescription(`<:approve:1006150867029864588>   Changed server's icon`)
                          let cant = new Discord.MessageEmbed()
                           .setColor(`FF0000`)
                           .setDescription(`<:warn:1006150861195587604>  Couldn't change the server's icon`)
                          message.guild.setIcon(`${argresult}`)
                          .then(nush => message.channel.send(changed))
                          .catch(error => { 
                            message.reply({embeds: [cant]});
                          })
             } else {
               const missingargs = new Discord.MessageEmbed()
            .setTitle(`Missing arguments`)
            .setDescription(`\`${prefix}setguildicon [image link]\``)
            .setColor(`FF0000`)
            message.reply({embeds: [missingargs]});
             }
            }
            }
            if(message.content.startsWith(`${prefix}setguildname`) || message.content.startsWith(`${prefix}setservername`)) {
              if (!message.guild.me.permissions.has('MANAGE_GUILD')) { 
                const perms = new Discord.MessageEmbed()
                .setColor(`FFF300`)
                .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`manage_server\``)
                message.reply({embeds: [perms]});
               }
              if (! message.member.permissions.has(['ADMINISTRATOR'])) {
                const missingperms = new Discord.MessageEmbed()
                .setColor(`FFF300`)
                .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`administrator\``)
                message.reply({embeds: [missingperms]});
            } else {
               args = message.content.split(" ").slice(1);
                         var argresult = args.join(' ');
                         if(argresult) {
                           let changed = new Discord.MessageEmbed()
                           .setColor(`0CFF00`)
                           .setDescription(`<:approve:1006150867029864588>   Changed server's name`)
                           let cant = new Discord.MessageEmbed()
                           .setColor(`FF0000`)
                           .setDescription(`<:deny:999025481183662110> Couldn't change the server's name`)
                          message.guild.setName(`${argresult}`)
                          .then(nush => message.channel.send(changed))
                          .catch(error => { 
                            message.reply({embeds: [cant]});
                          })
             } else {
               const missingargs = new Discord.MessageEmbed()
            .setTitle(`Missing arguments`)
            .setDescription(`\`${prefix}setguildname [name]\``)
            .setColor(`FF0000`)
            message.reply({embeds: [missingargs]});
             }
            }
            }
            if(message.content.startsWith(`${prefix}setguildbanner`) || message.content.startsWith(`${prefix}setserverbanner`)) {
                const noboost = new Discord.MessageEmbed()
                .setColor(`FFF300`)
                .setDescription(`<:warn:1006150861195587604>    This server needs to have at least 7 boosts in order to set a banner!`)
              if (!message.guild.me.permissions.has('MANAGE_GUILD')) { 
                const perms = new Discord.MessageEmbed()
                .setColor(`FFF300`)
      .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`manage_server\``)
                message.reply({embeds: [perms]});
               }
               if(message.guild.premiumSubscriptionCount < 7)  return message.reply(noboost)
              if (! message.member.permissions.has(['ADMINISTRATOR'])) {
                const missingperms = new Discord.MessageEmbed()
                .setColor(`FFF300`)
      .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`administrator\``)
                message.reply({embeds: [missingperms]});
            } else {
               args = message.content.split(" ").slice(1);
                         var argresult = args.join(' ');
                         if(argresult) {
                           let changed = new Discord.MessageEmbed()
                           .setColor(`0CFF00`)
                           .setDescription(`<:approve:1006150867029864588>   Changed server's banner`)
                           let cant = new Discord.MessageEmbed()
                           .setColor(`FF0000`)
                           .setDescription(`<:deny:999025481183662110> Couldn't change the server's banner`)
                          message.guild.setBanner(`${argresult}`)
                          .then(nush => message.channel.send(changed))
                           .catch(error => { 
                            message.reply({embeds: [cant]});
                          })
             } else {
               const missingargs = new Discord.MessageEmbed()
            .setDescription(`\`${prefix}setguildbanner [image link]\``)
            .setColor(`FF0000`)
            message.reply({embeds: [missingargs]});
             }
            }
            }
            /*


            SERVER RELATED


            */
    if(message.content.startsWith(`${prefix}poll`)) {
     if (! message.member.permissions.has('MANAGE_GUILD')) {
       const missingperms = new Discord.MessageEmbed()
       .setColor(`FFF300`)
       .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
       message.reply({embeds: [missingperms]});
  } else {
message.delete()
      args = message.content.split(" ").slice(1);
                var argresult = args.join(' ');
                if(argresult) {
      let embed = new Discord.MessageEmbed()
         .setTitle(`${argresult}`)
        .setColor("BLACK")
        .setDescription(`👍 - Yes

👎 - No`);
      let msg = await message.channel.send({embeds: [embed]});
      await msg.react("👍");
      await msg.react("👎");
    } else {
      const missingargs = new Discord.MessageEmbed()
  .setTitle(`Missing arguments`)
  .setDescription(`\`${prefix}poll [message]\``)
  .setColor(`FF0000`)
  message.reply({embeds: [missingargs]});
    }
  }
}
if (message.content.toLowerCase() === `${prefix}serverstats`) {
  const Embed = new Discord.MessageEmbed()
  .setTitle(`${message.guild.name}'s stats`)
  .setThumbnail(message.guild.iconURL({ dynamic: true}))
  .setColor(`BLACK`)
    .addField(`<:online:1016339811470168135>  Online Members`, `${message.guild.members.cache.filter(member => member.presence.status === "online").size}`, true)
    .addField("<:offline:1016339884425875536>  Offline Members", `${message.guild.members.cache.filter(member => member.presence.status === "offline").size}`, true)
    .addField("<:o_idle:1016339848522637333> Idle Members", `${message.guild.members.cache.filter(member => member.presence.status === "idle").size}`, true)
    .addField("<:o_dnd:1016339314092818502> Do not disturb Members", `${message.guild.members.cache.filter(member => member.presence.status === "dnd").size}`, true)


  .setFooter(`Requested by ${message.author.username}`, message.author.avatarURL({ dynamic: true}))
 message.reply({embeds: [Embed]});;
};
if(message.content === `${prefix}server` || message.content === `${prefix}serverinfo` || message.content === `${prefix}si`) {
const verificationLevels = {
    NONE: 'None',
    LOW: 'Low',
    MEDIUM: 'Medium',
    HIGH: '(╯°□°）╯︵ ┻━┻',
    VERY_HIGH: '┻━┻ ﾐヽ(ಠ益ಠ)ノ彡┻━┻'
};
const filterLevels = {
    DISABLED: 'Off',
    MEMBERS_WITHOUT_ROLES: 'No Role',
    ALL_MEMBERS: 'Everyone'
};
  const roles = message.guild.roles.cache.sort((a, b) => b.position - a.position).map(role => role.toString());
        const members = message.guild.members.cache;
        const channels = message.guild.channels.cache;
        const emojis = message.guild.emojis.cache;
 let rolesdisplay;
        
        if(roles.length < 20){
            rolesdisplay = roles.join(' ')
        } else {
            rolesdisplay = roles.slice(20).join(' ')
        }
    const { guild } = message
  const owner = (message.guild.owner = await message.guild
    .fetchOwner()
    .then((m) => m.user)
    .catch(() => { }));

        const embed = new MessageEmbed()
            .setTitle(`Info for ${message.guild.name}`)
            .setColor('BLACK')
            .setThumbnail(message.guild.iconURL({ dynamic: true }))
            .addField(`Owner`, `<:icons_owner:1018868665321525258> ${owner.tag}`, true)
            .addField(`Verification Level`, `<:approve:1006150867029864588> ${verificationLevels[message.guild.verificationLevel]}`, true)
            .addField(`Member Count`, `<:icons_user:1018869289870176357> ${message.guild.memberCount}`, true)
            .addField(`Channels`, ` <:suffer_channel:1006495811665940510> ${guild.channels.cache.size}  `, true)
            .addField(`Server prefix`, `<:icons_settings:1006151454505046056> ${prefix}`, true)
            .addField(`Boosts`, `<:icons_boost:1018872990043213914> ${message.guild.premiumSubscriptionCount || '0'}`, true)
            .addField(`Roles Count`, `<:icons_user:1018869289870176357> ${roles.length} roles`)
          .addField(`Explicit Filter`, `<:riot_nsfw:1018873240468328469> ${filterLevels[message.guild.explicitContentFilter]}`, true)
            .addField(`Server created`, `<:icons_bulb:1005306666939600956> ${moment(message.guild.createdTimestamp).format('LT')} ${moment(message.guild.createdTimestamp).format('LL')}\n[${moment(message.guild.createdTimestamp).fromNow()}]`, true)
            .setFooter(`ID: ${message.guild.id}`)
            .setTimestamp();
       message.reply({embeds: [embed]});;
    } 
    if(message.content.startsWith(`${prefix}tts`)) {
      const missingperms = new Discord.MessageEmbed()
      .setColor(`FFF300`)
      .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`send_tts_messages\``)
      const botmissingperms = new Discord.MessageEmbed()
      .setColor(`FFF300`)
      .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`send_tts_messages\``)
      const missingargs = new Discord.MessageEmbed()
      .setTitle("Missing arguments!")
      .setColor(`FF0000`)
      .setDescription(`\`${prefix}tts [message]\``)
      var params = message.content.substring().split(" ");
      let msg = params.slice(1).join(' ');
      if(! message.member.permissions.has('SEND_TTS_MESSAGES')) return message.reply({embeds: [missingperms]});
      if(!message.guild.me.permissions.has('SEND_TTS_MESSAGES')) return message.reply({embeds: [botmissingperms]});
      if(!msg) return message.reply({embeds: [missingargs]});
      if(msg.includes('discord.gg') || msg.includes('http://') || msg.includes('https://') || msg.includes('www.') || msg.includes('./gg')) return message.channel.send(`<@${message.author.id}> **Don't text to speech a link!** <a:suffer_texting:1006495813381390369>`)
      message.channel.send(`${msg}`, {
        tts: true
       })
    }
    /*


    BAN UNBAN KICK


    */
    if (message.content.startsWith(`${prefix}ban`) && !message.content.includes(`${prefix}banner`)) {
      const missingperms = new Discord.MessageEmbed()
      .setColor(`FFF300`)
      .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`ban_members\``)
        const perms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
            .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`ban_members\``)
      if (! message.member.permissions.has('BAN_MEMBERS')) return message.reply({embeds: [missingperms]});
  if (!message.guild.me.permissions.has('BAN_MEMBERS')) return message.reply({embeds: [perms]});
  if (message.mentions.users.size === 0 && message.member.permissions.has('BAN_MEMBERS') && message.content === `${prefix}ban`) { 
    const missingargs = new Discord.MessageEmbed()
    .setTitle(`Missing arguments`)
    .setDescription(`\`${prefix}ban [user mention / user id] [reason (optional)]\``)
    .setColor(`FF0000`)
    message.reply({embeds: [missingargs]});}
    var params = message.content.substring().split(" ");
      let banMember = message.mentions.members.first() || message.guild.members.cache.get(params[1]);
  let reasonName = params.slice(2).join(' ')
  if(!reasonName) reasonName = 'No reason provided'
  if (!banMember && message.content.startsWith(`;banner`)) return;
  const hieracy = new Discord.MessageEmbed()
          .setColor(`FF0000`)
          .setDescription(`<:deny:999025481183662110> you can't ban someone with an equal or higher role`)
      if (!message.member.permissions.has("BAN_MEMBERS")) return message.channel.send({embeds: [hieracy]})
  if(banMember) {
          banMember
          .ban({
            days: 7,
            reason: `${reasonName}`
          })
          .then((member) => {                              
            const succes = new Discord.MessageEmbed()
            .setTitle(`Banned succsesfully!`)
            .setColor(`0CFF00`)
            .setDescription(banMember.displayName + "#" + banMember.user.discriminator + " has been successfully banned")
            .setThumbnail(banMember.user.displayAvatarURL({ dynamic: true}))
              .addFields(
                { name: 'Moderator:', value: `${message.author}` },
                { name: 'Member:', value: `${banMember}` },
                { name: 'Reason:', value: `${reasonName}` },
              )
            message.reply({embeds: [succes]})

            const dms = new Discord.MessageEmbed()
            .setTitle(`Ban case`)
            .setColor(`FF0000`)
            .setDescription(`You were banned from **${message.guild.name}**`)
            .setThumbnail(message.guild.iconURL({
              dynamic: true
            }))
              .addFields(
                { name: 'Moderator:', value: `${message.author}` },
                { name: 'Reason:', value: `${reasonName}`, inline: true },
              )
            .setFooter(`If you would like to dispute this punishment, contact a staff member.`)
            .setTimestamp()
            banMember.send({ embeds: [dms] }).catch(error => {
              console.log(console.error)
            })
          })
      }
    }





      if(message.content.startsWith(`${prefix}unban`)) {
          const missingperms = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`ban_members\``)
    
            const perms = new Discord.MessageEmbed()
            .setColor(`FFF300`)
            .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`ban_members\``)

            const missingargs = new Discord.MessageEmbed()
            .setTitle(`Missing arguments`)
            .setDescription(`\`${prefix}unban [user id]\``)
            .setColor(`FF0000`)
          const cant = new Discord.MessageEmbed()
          .setColor(`FF0000`)
          .setDescription(`<:deny:999025481183662110> Couldn't unban member`)
          if (! message.member.permissions.has('BAN_MEMBERS')) return message.reply({embeds: [missingperms]});
      if (!message.guild.me.permissions.has('BAN_MEMBERS')) return message.reply({embeds: [perms]});
      var params = message.content.substring().split(" ");
      let banMember = params[1];
      if (!banMember) return message.reply({embeds: [missingargs]}); 
      message.guild.members.unban(banMember).catch(error => message.channel.send(cant))
      message.reply(`👍`)
      }
      if (message.content.startsWith(`${prefix}kick`)) {
        const perms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`kick_members\``)

        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`kick_members\``)
        if (! message.member.permissions.has('KICK_MEMBERS')) return message.reply({embeds: [missingperms]});
    if (!message.guild.me.permissions.has('KICK_MEMBERS')) return message.reply({embeds: [perms]});
    if (message.mentions.users.size === 0 && message.member.permissions.has('KICK_MEMBERS') && message.content === `${prefix}kick`) { 
      const missingargs = new Discord.MessageEmbed()
      .setTitle(`Missing arguments`)
      .setDescription(`\`${prefix}kick [user mention / user id] [reason (optional)]\``)
      .setColor(`FF0000`)
      message.reply({embeds: [missingargs]});}
      var params = message.content.substring().split(" ");
        let kickMember = message.mentions.members.first() || message.guild.members.cache.get(params[1]);
    let reasonName = params.slice(2).join(' ')
    if(!reasonName) reasonName = 'No reason provided'
    const hieracy = new Discord.MessageEmbed()
          .setColor(`FF0000`)
          .setDescription(`<:deny:999025481183662110> you can't kick someone with an equal or higher role`)
        if (!message.member.permissions.has("BAN_MEMBERS")) return message.channel.send({embeds: [hieracy]})
    if (!kickMember) return;
    if(kickMember) {
            kickMember
            .kick()
            .then((member) => {
              const succes = new Discord.MessageEmbed()
              .setTitle(`Kicked succsesfully!`)
              .setColor(`0CFF00`)
              .setDescription(kickMember.displayName + "#" + kickMember.user.discriminator + " has been successfully kicked")
              .setThumbnail(kickMember.user.displayAvatarURL({ dynamic: true}))
              .addField("Moderator", message.author)
              .addField("Member", kickMember)
              .addField("Reason", reasonName)
              message.reply(succes)

              const dms = new Discord.MessageEmbed()
            .setTitle(`Kick case`)
            .setColor(`FF0000`)
            .setDescription(`You were kicked from **${message.guild.name}**`)
            .setThumbnail(message.guild.iconURL({
              dynamic: true
            }))
            .addField("Moderator", message.author)
            .addField("Reason", reasonName)
            .setFooter(`If you would like to dispute this punishment, contact a staff member.`)
            .setTimestamp()
            kickMember.send({embeds: [dms]}).catch(error => {
              console.log(console.error)
            })
            })
          }
        }
        /*


        ROLE ADD ROLE REMOVE


        */
        if(message.content.startsWith(`${prefix}role+`) || message.content.startsWith(`${prefix}roleadd`)) {
          const missingperms = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_roles\``)

          const missingargs = new Discord.MessageEmbed()
          .setTitle(`Missing arguments!`)
          .setColor(`FF0000`)
          .setDescription(`\`${prefix}role+ [user mention / user id] [role name / role id]\``)

          const cant = new Discord.MessageEmbed()
          .setColor(`FF0000`)
          .setDescription(`<:warn:1006150861195587604>  Couldn't add role to the user`)

          const hieracy = new Discord.MessageEmbed()
          .setColor(`FF0000`)
          .setDescription(`<:warn:1006150861195587604>  ${message.author}: You cannot role someone with an equal or higher role`)

          if(! message.member.permissions.has(`MANAGE_ROLES`)) return message.reply({embeds: [missingargs]});
          if(!message.guild.me.permissions.has(`MANAGE_ROLES`)) return message.reply({embeds: [missingargs]});
          var params = message.content.substring().split(" ");
                    params[0] = params[0].toLowerCase();
          const user = message.mentions.members.first() || message.guild.members.cache.get(params[1])
          if(!user) return message.reply({embeds: [missingargs]});
          if (user.roles.highest.position >= message.member.roles.highest.position && message.author.id !== message.guild.owner) return message.channel.send(hieracy);
          var rolename = params.slice(2).join(' ') || message.guild.roles.cache.get(params[2])
          if(!rolename) return message.reply({embeds: [missingargs]});
          var role;
          if (params.slice(2).join(' ')) role = user.guild.roles.cache.find(role => role.name.includes(`${rolename}`))
          if (message.guild.roles.cache.get(params[2])) role = user.guild.roles.cache.find(role => role.id == `${rolename}`)
          user.roles.add(role)
          .catch( error => {
            message.channel.send(cant)
          })
          let succes = new Discord.MessageEmbed()
          .setColor(`0CFF00`)
          .setDescription(`<:approve:1006150867029864588>   added ${role} to ${user}`)
          message.reply(succes)
        }
        if(message.content.startsWith(`${prefix}role-`) || message.content.startsWith(`${prefix}rolermv`) || message.content.startsWith(`${prefix}roleremove`)) {
          const missingperms = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_roles\``)

          const missingargs = new Discord.MessageEmbed()
          .setTitle(`Missing arguments!`)
          .setColor(`FF0000`)
          .setDescription(`\`${prefix}role- [user mention / user id] [role name / role id]\``)

          const cant = new Discord.MessageEmbed()
          .setColor(`FF0000`)
          .setDescription(`<:deny:999025481183662110> Couldn't remove role from the user`)

          const hieracy = new Discord.MessageEmbed()
          .setColor(`FF0000`)
          .setDescription(`<:deny:999025481183662110> ${message.author}: You cannot remove role from someone with an equal or higher role`)
          if(! message.member.permissions.has(`MANAGE_ROLES`)) return message.reply({embeds: [missingperms]});
          if(!message.guild.me.permissions.has(`MANAGE_ROLES`)) return message.reply({embeds: [missingperms]});
          var params = message.content.substring().split(" ");
                    params[0] = params[0].toLowerCase();
          const user = message.mentions.members.first() || message.guild.members.cache.get(params[1])
          if(!user) return message.reply({embeds: [missingargs]});
          if (user.roles.highest.position >= message.member.roles.highest.position && message.author.id !== message.guild.owner.id) return message.channel.send(hieracy);
          var rolename = params.slice(2).join(' ') || message.guild.roles.cache.get(params[2])
          if(!rolename) return message.reply({embeds: [missingargs]});
          var role;
          if(params.slice(2).join(' ')) role = user.guild.roles.cache.find(role => role.name.includes(`${rolename}`))
          if(message.guild.roles.cache.get(params[2])) role = user.guild.roles.cache.find(role => role.id == `${rolename}`)
          user.roles.remove(role)
          .catch( error => {
            message.channel.send(cant)
          })
          const success = new Discord.MessageEmbed()
          .setDescription(`<:approve:1006150867029864588>   removed ${role} from ${user}`)
          .setColor(`0CFF00`)
          message.reply(success)
        }
        if(message.content === `${prefix}role`) {
          const missingperms = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_roles\``)
          if(! message.member.permissions.has(`MANAGE_ROLES`)) return message.reply({embeds: [missingperms]});
          if(!message.guild.me.permissions.has(`MANAGE_ROLES`)) return message.reply({embeds: [missingperms]});
          const missingargs = new Discord.MessageEmbed()
          .setTitle(`Missing arguments!`)
          .setColor(`FF0000`)
          .setDescription(` \`${prefix}role+/- [user id / user mention] [role]\`
**Example:**

${prefix}role+ Remain#1000 staff or ${prefix}role+ 985904723456577546 staff
(adds role to user)

${prefix}role- Remain#1000 special or ${prefix}role- 985904723456577546 special
(removes role from user)

Aliases: \`roleadd\`, \`roleremove\`, \`rolermv\``)
message.reply({embeds: [missingargs]});
        }
         /*


        SERVER CONFIGURATION


        */
       if(message.content.startsWith(`${prefix}setautoresponder`)) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setautoresponder [trigger] [response]\`\n\ntrigger = message that triggers the bot's response\nresponse = bot's response`)
        if(! message.member.permissions.has('MANAGE_GUILD')) return message.reply({embeds: [missingperms]});
        var args = message.content.substring().split(" ");
        let trigger = args[1]
        let response = args.slice(2).join(' ');
        if(!trigger) return message.reply({embeds: [missingargs]});
        if(!response) return message.reply({embeds: [missingargs]});
        db.set(message.guild.id + trigger + 'autoresponder', response)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   set autoresponder with trigger (${trigger}) and response (${response})`)
       message.reply({embeds: [can]});
       const candms = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   set autoresponder with trigger (${trigger}) and response (${response}) in ${message.guild.name}`)
         message.guild.owner.send({ embeds: [candms]}).catch(error => {
console.log(console.error)
})
       }
       if(message.content.startsWith(`${prefix}delautoresponder`) || message.content.startsWith(`${prefix}deleteautoresponder`)) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)

        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}deleteautoresponder [trigger]\``)

        const missingres = new Discord.MessageEmbed()
        .setColor(`FF0000`)
        .setDescription(`<:deny:999025481183662110> there is no autoresponder with this trigger`)
          if(! message.member.permissions.has('MANAGE_GUILD')) return message.reply({embeds: [missingperms]});
        var args = message.content.substring().split(" ");
        let trigger = args.slice(1).join(" ")
        if(!trigger) return message.reply({embeds: [missingargs]});
        let auto = db.fetch(message.guild.id + trigger + 'autoresponder')
        if(!auto) return message.channel.send(missingres)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   deleted autoresponder with trigger (${trigger}) and response (${auto})`)
       const candms = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   deleted autoresponder with trigger (${trigger}) and response (${auto}) in ${message.guild.name}`)
        db.delete(message.guild.id + trigger + 'autoresponder')
        message.reply({embeds: [can]});
         message.channel.send({embeds: [candms]}).catch(error => {
console.log(console.error)
})
       }
       if(message.content.startsWith(`${prefix}setautorole bots`)) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)

        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setautorole bots [role mention / role id]\``)

        if(! message.member.permissions.has('MANAGE_SERVER') || !message.guild.me.permissions.has('MANAGE_ROLES')) return message.reply({embeds: [missingperms]});
        var args = message.content.substring().split(" ");
        const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[2]);
        if(!role) return message.reply({embeds: [missingargs]});
        db.fetch(`autorole_bots_${message.guild.id}`)
        db.set(`autorole_bots_${message.guild.id}`, role.id);
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   ${role} added as autorole for bots`)
       message.reply({embeds: [can]});
       }
       if(message.content.startsWith(`${prefix}deleteautorole bots`) || message.content.startsWith(`${prefix}delautorole bots`)) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)

        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}deleteautorole bots [role mention / role id]\``)

        if(! message.member.permissions.has('MANAGE_GUILD') || !message.guild.me.permissions.has('MANAGE_ROLES')) return message.reply({embeds: [missingperms]});
        var args = message.content.substring().split(" ");
        const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[2]);
        if(!role) return message.reply({embeds: [missingargs]});
        db.fetch(`autorole_bots_${message.guild.id}`)
        db.delete(`autorole_bots_${message.guild.id}`, role.id)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   ${role} removed from autorole for bots`)
        message.reply({embeds: [can]});
       }
       if(message.content.startsWith(`${prefix}setautorole humans`)) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)

        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setautorole humans [role mention / role id]\``)

        if(! message.member.permissions.has('MANAGE_SERVER') || !message.guild.me.permissions.has('MANAGE_ROLES')) return message.reply({embeds: [missingperms]});
        var args = message.content.substring().split(" ");
        const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[2]);
        if(!role) return message.reply({embeds: [missingargs]});
        db.fetch(`autorole_${message.guild.id}`)
        db.set(`autorole_${message.guild.id}`, role.id);
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   ${role} added as autorole for humans`)
       message.reply({embeds: [can]});
       }
       if(message.content.startsWith(`${prefix}deleteautorole humans`) || message.content.startsWith(`${prefix}delautorole humans`)) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)

        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}deleteautorole humans [role mention / role id]\``)

        if(! message.member.permissions.has('MANAGE_GUILD') || !message.guild.me.permissions.has('MANAGE_ROLES')) return message.reply({embeds: [missingperms]});
        var args = message.content.substring().split(" ");
        const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[2]);
        if(!role) return message.reply({embeds: [missingargs]});
        db.fetch(`autorole_${message.guild.id}`)
        db.delete(`autorole_${message.guild.id}`, role.id)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   ${role} removed from autorole for humans`)
        message.reply({embeds: [can]});
       }
       if(message.content === `${prefix}autorole list`) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingch = new Discord.MessageEmbed()
        .setColor(`FF0000`)
        .setDescription(`<:deny:999025481183662110> There are no roles marked as auto role!`)
        if(! message.member.permissions.has('MANAGE_GUILD') || !message.guild.me.permissions.has('MANAGE_ROLES')) return message.reply({embeds: [missingperms]});
        let rolz = db.fetch(`autorole_${message.guild.id}`)
        let rolez = db.fetch(`autorole_bots_${message.guild.id}`)
        if(!rolz && !rolez) return message.reply({embeds: [missingch]});
        let humans = `<@&${rolz}>`
        let botz = `<@&${rolez}>`
        if(!rolz) humans = "None"
        if(!rolez) botz = "None"
        const embed = new Discord.MessageEmbed()
        .setColor(`BLACK`)
        .setTitle(`Autorole list for ${message.guild.name}`)
        .setThumbnail(message.guild.iconURL({ dynamic: true}))
        .setDescription(`**Humans autorole**\n${humans}\n\n**Bots Autorole**\n${botz}`)
        .setFooter(`Requested by ${message.author.username}`, message.author.avatarURL({ dynamic: true}))
        .setTimestamp()
       message.reply({embeds: [embed]});
       }
       if(message.content.toLowerCase() === `${prefix}setautorole`) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setColor(`FF0000`)
        .setDescription(`${prefix}setautorole humans [role id / role mention - sets autorole for regular users\n${prefix}setautorole bots [role id / role mention] - sets autorole for bots`)
        if(! message.member.permissions.has('MANAGE_GUILD')) return message.reply({embeds: [missingperms]});
        message.reply({embeds: [missingargs]});
       }
       if(message.content.startsWith(`${prefix}setpingonjoin`)) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)

        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setpingonjoin [channel mention / channel id]\``)
        if(! message.member.permissions.has('MANAGE_GUILD') || !message.guild.me.permissions.has('MANAGE_GUILD')) return message.reply({embeds: [missingperms]});
        var args = message.content.substring().split(" ");
        const channel = message.mentions.channels.first() || message.guild.channels.cache.get(args[1]);
        if(!channel) return message.reply({embeds: [missingargs]});
        db.fetch(`pingonjoin_${message.guild.id}`)
        db.set(`pingonjoin_${message.guild.id}`, channel.id)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   Pinging new members in ${channel}! Make sure the bot can send messages in the mentioned channel!`)
        message.reply({embeds: [can]});
       }
       if(message.content.startsWith(`${prefix}deletepingonjoin`) || message.content.startsWith(`${prefix}delpingonjoin`)) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)

        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}deletepingonjoin [channel mention / channel id]\``)
        if(! message.member.permissions.has('MANAGE_GUILD') || !message.guild.me.permissions.has('MANAGE_GUILD')) return message.reply({embeds: [missingperms]});
        var args = message.content.substring().split(" ");
        const channel = message.mentions.channels.first() || message.guild.channels.cache.get(args[1]);
        if(!channel) return message.reply({embeds: [missingargs]});
        db.fetch(`pingonjoin_${message.guild.id}`)
        db.delete(`pingonjoin_${message.guild.id}`, channel.id)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   I will not ping new members anymore in ${channel} `)
        message.reply({embeds: [can]});
       }
       if(message.content === `${prefix}pingonjoin list`) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingch = new Discord.MessageEmbed()
        .setColor(`FF0000`)
        .setDescription(`<:deny:999025481183662110> There are no channels where new members are pinged!`)
        if(! message.member.permissions.has('MANAGE_GUILD') || !message.guild.me.permissions.has('MANAGE_GUILD')) return message.reply({embeds: [missingperms]});
        let ch = db.fetch(`pingonjoin_${message.guild.id}`)
        if(!ch) return message.reply({embeds: [missingch]});
        const embed = new Discord.MessageEmbed()
        .setColor(`BLACK`)
        .setTitle(`Ping on join channels from ${message.guild.name}`)
        .setDescription(`<#${ch}>`)
        .setThumbnail(message.guild.iconURL({ dynamic: true}))
        .setFooter(`Requested by ${message.author.username}`, message.author.displayAvatarURL({ dynamic: true}))
        .setTimestamp()
       message.reply({embeds: [embed]});
       }
       if(message.content.startsWith(`${prefix}setjoindm`)) {
        args = message.content.split(" ").slice(1);
        let joindm = args.join(' ')
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setjoindm [message]\``)
      if(! message.member.permissions.has('MANAGE_GUILD')) return message.reply({embeds: [missingperms]});
      if(!joindm) return message.reply({embeds: [missingargs]});
      let sending = joindm.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?mention`?/g, `<@${message.author.id}>`).replace(/`?\?rank`?/g, message.guild.memberCount)
       db.fetch(`joindm_${message.guild.id}`)
       db.set(`joindm_${message.guild.id}`, sending)
       const can = new Discord.MessageEmbed()
       .setColor(`0CFF00`)
       .setDescription(`<:approve:1006150867029864588>   Set the join dm message! Type \`;joindm message\` to see your message!`)
       message.reply({embeds: [can]});
       }
       if(message.content === `${prefix}deletejoindm` || message.content === `${prefix}deljoindm`) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingch = new Discord.MessageEmbed()
        .setColor(`FF0000`)
        .setDescription(`<:deny:999025481183662110> There is no message to send in dm's`)
        if(! message.member.permissions.has('MANAGE_GUILD')) return message.reply({embeds: [missingperms]});
        let ver = db.fetch
        if(!ver) return message.channel.send(missingch)
        db.delete(`joindm_${message.guild.id}`)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   Deleted the message from join dm!`)
        message.reply({embeds: [can]});
       }
       if(message.content === `${prefix}joindm message`) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingch = new Discord.MessageEmbed()
        .setColor(`FF0000`)
        .setDescription(`<:deny:999025481183662110> There is no message to send in dm's`)
        if(! message.member.permissions.has('MANAGE_GUILD')) return message.reply({embeds: [missingperms]});
        let mes = db.fetch(`joindm_${message.guild.id}`)
        if(!mes) return message.reply({embeds: [missingch]});
        const embed = new Discord.MessageEmbed()
        .setColor(`BLACK`)
        .setTitle(`Join dm message in ${message.guild.name}`)
        .setDescription(`\`\`\`${mes}\`\`\``)
        .setThumbnail(message.guild.iconURL({ dynamic: true}))
        .setFooter(`Requested by ${message.author.username}`, message.author.displayAvatarURL({ dynamic: true}))
        .setTimestamp()
       message.reply({embeds: [embed]});
       }
       /*


       SET WELCOME


       */
      if(message.content.toLowerCase().startsWith(`${prefix}setwelcomechannel`)) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setwelcomechannel [channel mention]\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        let channel = message.mentions.channels.first()
        if(!channel) return message.reply({embeds: [missingargs]});
        db.set(`welcome_${message.guild.id}`, channel.id)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   Welcome channel updated as ${channel}`)
        message.reply({embeds: [can]});
      }
      if(message.content.toLowerCase().startsWith(`${prefix}setwelcomethumbnail`)) {
        var args = message.content.substring().split(" ");
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setwelcomethumbnail [image link / variable]\`\n\`?useravatar\ to display user avatar or \`?serveravatar\` to display server avatar in thumbnail`)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        const text = args.slice(1).join(" ");
  if (!text || text.length > 1000) return message.reply({embeds: [missingargs]});
  if(text === "none") {
    db.delete(`thumbnail_${message.guild.id}`)
    const can = new Discord.MessageEmbed()
.setColor(`0CFF00`)
.setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted thumbnail from welcome message embed`)
message.reply({embeds: [can]});
  } else {
  db.set(`thumbnail_${message.guild.id}`, text)
  message.channel.send(`Now welcome thumbnail will be \n \`${text}\` `)
  }
      }
      if(message.content.toLowerCase().startsWith(`${prefix}setwelcomeimage`)) {
        var args = message.content.substring().split(" ");
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setwelcomeimage [image link]\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        const text = args.slice(1).join(" ");
  if (!text || text.length > 1000) return message.reply({embeds: [missingargs]});
if(text === "none") {
db.delete(`image_${message.guild.id}`)
const can = new Discord.MessageEmbed()
.setColor(`0CFF00`)
.setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted image from welcome message embed`)
message.reply({embeds: [can]});
} else {
  db.set(`image_${message.guild.id}`, text)
    message.channel.send(`Now welcome image will be \n \`${text}\` `)
}
      }
      if(message.content.toLowerCase().startsWith(`${prefix}setwelcomedescription`)) {
        var args = message.content.substring().split(" ");
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setwelcomedescription [message]\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        const text = args.slice(1).join(" ");
  if (!text || text.length > 1024) return message.reply({embeds: [missingargs]});
  db.set(`desc_${message.guild.id}`, text)
  let mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?mention`?/g, `<@${message.author.id}>`)
  const can = new Discord.MessageEmbed()
  .setColor(`0CFF00`)
  .setDescription(`<:approve:1006150867029864588>   ${message.author}: Now in welcome message description will be \n \`${mes}\` `)
  message.reply({embeds: [can]});
      }
      if(message.content.toLowerCase().startsWith(`${prefix}setwelcomecolor`)) {
        var args = message.content.substring().split(" ");
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setwelcomecolor [color name in caps / hex code]\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        const text = args.slice(1).join(" ");
        if (!text || text.length > 6) return message.reply({embeds: [missingargs]});
        let upe = text.toUpperCase()
        db.set(`color_${message.guild.id}`, upe)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   ${message.author}: Color set as ${upe}`)
        message.reply({embeds: [can]});
      }
      if(message.content.toLowerCase() === `${prefix}delwelcome` || message.content.toLowerCase() === `${prefix}deletewelcome`) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        db.delete(`welcome_${message.guild.id}`);
        db.delete(`desc_${message.guild.id}`)
        db.delete(`image_${message.guild.id}`)
        db.delete(`thumbnail_${message.guild.id}`)
        db.delete(`color_${message.guild.id}`)
        db.delete(`title_${message.guild.id}`)
        db.delete(`footer_${message.guild.id}`)
        db.delete(`welcometop_${message.guild.id}`)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted the welcome message`)
        message.reply({embeds: [can]});
      }
      if(message.content.toLowerCase() === `${prefix}testwelcome`) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        let chreq = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author} channel isn't configuFF0000`)
        let desreq = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author} description isn't configuFF0000`)
        let plaine = db.fetch(`welcometop_${message.guild.id}`)
        let channel = db.get(`welcome_${message.guild.id}`);
        let text = db.get(`desc_${message.guild.id}`)
         let img = db.get(`image_${message.guild.id}`)
         let nail = db.get(`thumbnail_${message.guild.id}`)
         let me = db.get(`mention_${message.guild.id}`)
         let tit =  db.fetch(`title_${message.guild.id}`)
         let col = db.fetch(`color_${message.guild.id}`)
         let fot = db.fetch(`footer_${message.guild.id}`)
         let titlol
         let tnail
         let mes
         let foter
         let isplaine
         if(!channel) message.reply({embeds: [chreq]});
         if(!col) col = "RANDOM"
         if(tit) titlol = tit.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag)
         if(!tit) titlol = " "
         if(!text) return message.reply({embeds: [desreq]});
         if(text) mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?mention`?/g, `<@${message.author.id}>`).replace(/`?\?rank`?/g, message.guild.memberCount);
         if(!fot) foter = " "
         if(fot) foter = fot.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?rank`?/g, message.guild.memberCount)
if(nail) tnail = nail.replace(/`?\?useravatar`?/g, message.author.displayAvatarURL({ dynamic: true })).replace(/`?\?serveravatar`?/g, message.guild.iconURL({ dynamic: true }))
if(!nail) tnail = " "
if(!plaine) isplaine = " "
if(plaine) isplaine = plaine.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?rank`?/g, message.guild.memberCount).replace(/`?\?mention`?/g, message.author)
const embed = new Discord.MessageEmbed()
.setTitle(`${titlol}`)
.setDescription(`${mes}`)
.setColor(`${col}`)
.setImage(img)
.setThumbnail(tnail)
.setFooter(`${foter}`)
client.channels.cache.get(channel).send(isplaine, {
  embed: embed
})
      }
      if(message.content.toLowerCase().startsWith(`${prefix}setwelcometitle`)) {
        var args = message.content.substring().split(" ");
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setwelcometitle [message]\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        const text = args.slice(1).join(" ");
  if (!text || text.length > 1024) return message.reply({embeds: [missingargs]});
  if(text === "none") {
    db.delete(`title_${message.guild.id}`)
    const can = new Discord.MessageEmbed()
    .setColor(`0CFF00`)
    .setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted title from the welcome message`)
    message.reply({embeds: [can]});
  } else {
  db.set(`title_${message.guild.id}`, text)
  let mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?rank`?/g, message.guild.memberCount)
  const can = new Discord.MessageEmbed()
  .setColor(`0CFF00`)
  .setDescription(`<:approve:1006150867029864588>   ${message.author}: Now in welcome message title will be \n ${mes} `)
  message.reply({embeds: [can]});
  }
      }
      if(message.content.toLowerCase().startsWith(`${prefix}setwelcomefooter`)) {
        var args = message.content.substring().split(" ");
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setwelcomefooter [message]\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        const text = args.slice(1).join(" ");
  if (!text || text.length > 1024) return message.reply({embeds: [missingargs]});
  if(text === "none") {
    db.delete(`footer_${message.guild.id}`)
    const can = new Discord.MessageEmbed()
.setColor(`0CFF00`)
.setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted footer from welcome message embed`)
message.reply({embeds: [can]});
  } else {
    db.set(`footer_${message.guild.id}`, text)
    let mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?rank`?/g, message.guild.memberCount)
  const can = new Discord.MessageEmbed()
  .setColor(`0CFF00`)
  .setDescription(`<:approve:1006150867029864588>   ${message.author}: Now in welcome message footer will be \n \`${mes}\` `)
  message.reply({embeds: [can]});
  }
      }
      if(message.content.toLowerCase().startsWith(`${prefix}setwelcomemessage`)) {
        var args = message.content.substring().split(" ");
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setwelcomefooter [message]\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        const text = args.slice(1).join(" ");
  if (!text || text.length > 1024) return message.reply({embeds: [missingargs]});
  if(text === "none") {
    db.delete(`welcometop_${message.guild.id}`)
    const can = new Discord.MessageEmbed()
.setColor(`0CFF00`)
.setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted message from welcome message embed`)
message.reply({embeds: [can]});
  } else {
    db.set(`welcometop_${message.guild.id}`, text)
    let mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?rank`?/g, message.guild.memberCount).replace(/`?\?mention`?/g, message.author)
  const can = new Discord.MessageEmbed()
  .setColor(`0CFF00`)
  .setDescription(`<:approve:1006150867029864588>   ${message.author}: Now in welcome message will be \n \`${mes}\` `)
  message.reply({embeds: [can]});
  }
      }
      if(message.content.toLowerCase() === (`${prefix}welcome variables`)) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        let variables = new Discord.MessageEmbed()
        .setAuthor(message.author.tag, message.author.displayAvatarURL({ dynamic: true }))
        .setColor(`BLACK`)
        .setTitle(`Welcome message variables`)
        .setDescription(`?server - shows server name 
?tag shows member's full name - wintrs#2000
?mention - mentions new user - @wintrs
?user - shows new user username - wintrs
?useravatar - shows user's avatar
?serveravatar - shows server's avatar
?rank - shows join position - 30th member
`)
message.reply({embeds: [variables]});      }
      if(message.content.toLowerCase() === `${prefix}welcome` || message.content.toLowerCase() === `${prefix}help welcome`) {
        const helpwelcome = new Discord.MessageEmbed()
        .setAuthor(message.author.tag, message.author.displayAvatarURL({ dynamic: true }))
        .setTitle(`Welcome setup help`)
        .setColor(`BLACK`)
        .addField(`Welcome embed commands`, `${prefix}setwelcomechannel - sets welcome channel (requieFF0000)\n${prefix}setwelcometitle - sets welcome message title\n${prefix}setwelcomecolor - sets welcome message color (can be an hex code or color name only, otherwise this module might have errors)\n${prefix}setwelcomedescription - sets welcome description (requieFF0000)\n${prefix}setwelcomethumbnail - sets welcome messsage thumbnail\n${prefix}setwelcomeimage - sets welcome message image\n${prefix}setwelcomefooter - sets welcome message footer\n${prefix}setwelcomemessage - sets normal welcome message above the embed\n${prefix}testwelcome - sends welcome message`)
        .addField(`Welcome plain commands`, `${prefix}setplainwelcome - sets message for plain welcome message\n${prefix}setwelcomeplainchannel - sets channel to send plain welcome message\n${prefix}testplainwelcome - sends plain welcome message\n${prefix}deleteplainwelcome - deletes plain welcome message`)
        .addField(`Welcome variables`, `?server - shows server name 
?tag - shows member's full name - wintrs#2000
?mention - mentions new user - @wintrs
?user - shows new user username - wintrs
?useravatar - shows user's avatar
?serveravatar - shows server's avatar
?rank - shows join position - 30th member`)
        message.reply({embeds: [helpwelcome]});
      }
      if(message.content.toLowerCase().startsWith(`${prefix}setplainwelcome`)) {
        var args = message.content.substring().split(" ");
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setwelcometitle [message]\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        const text = args.slice(1).join(" ");
  if (!text || text.length > 1024) return message.reply({embeds: [missingargs]});
  if(text === "none") {
    db.delete(`welcomeplain_${message.guild.id}`)
    const can = new Discord.MessageEmbed()
    .setColor(`0CFF00`)
    .setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted welcome plain message`)
    message.reply({embeds: [can]});
  } else {
    let mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?rank`?/g, message.guild.memberCount).replace(/`?\?mention`?/g, `${message.author}`)
    db.set(`welcomeplain_${message.guild.id}`, text)
    const can = new Discord.MessageEmbed()
    .setColor(`0CFF00`)
    .setDescription(`<:approve:1006150867029864588>   ${message.author}: Plain welcome message set as:\n${mes}`)
    message.reply({embeds: [can]});
  }
      }
      if(message.content.toLowerCase().startsWith(`${prefix}setwelcomeplainchannel`)) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setwelcomeplainchannel [channel mention]\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        let channel = message.mentions.channels.first()
        if(!channel) return message.reply({embeds: [missingargs]});
        db.set(`welcomeplainchannel_${message.guild.id}`, channel.id)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   Welcome channel updated as ${channel}`)
        message.reply({embeds: [can]});
      }
      if(message.content.toLowerCase() === `${prefix}testplainwelcome`) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        let chreq = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author} channel isn't configuFF0000`)
        let desreq = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author} message isn't configuFF0000`)
        let channel = db.fetch(`welcomeplainchannel_${message.guild.id}`)
        let text = db.fetch(`welcomeplain_${message.guild.id}`)
        if(!channel) return message.reply({embeds: [chreq]});
        if(!text) return message.reply({embeds: [desreq]});
        let mes
        if(text) mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?mention`?/g, `<@${message.author.id}>`).replace(/`?\?rank`?/g, message.guild.memberCount);
        client.channels.cache.get(channel).send(mes)
      }
      if(message.content.toLowerCase() === `${prefix}delplainwelcome` || message.content.toLowerCase() === `${prefix}deleteplainwelcome`) {
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        db.delete(`welcomeplainchannel_${message.guild.id}`)
        db.delete(`welcomeplain_${message.guild.id}`)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted the welcome plain message`)
        message.reply({embeds: [can]});
      }
      /*


      SET BOOST MESSAGE


      */
     if(message.content.toLowerCase().startsWith(`${prefix}setboostchannel`)) {
      const missingperms = new Discord.MessageEmbed()
      .setColor(`FFF300`)
      .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
      const missingargs = new Discord.MessageEmbed()
      .setTitle(`Missing arguments!`)
      .setColor(`FF0000`)
      .setDescription(`\`${prefix}setboostchannel [channel mention]\``)
      if (!message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
      let channel = message.mentions.channels.first()
      if(!channel) return message.reply({embeds: [missingargs]});
      db.set(`boostchannel_${message.guild.id}`, channel.id)
      const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   ${message.author}: Boost channel set as ${channel}`)
        message.reply({embeds: [can]});
     }
     if(message.content.toLowerCase().startsWith(`${prefix}setboosttitle`)) {
      var args = message.content.substring().split(" ");
      const missingperms = new Discord.MessageEmbed()
      .setColor(`FFF300`)
      .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
      const missingargs = new Discord.MessageEmbed()
      .setTitle(`Missing arguments!`)
      .setColor(`FF0000`)
      .setDescription(`\`${prefix}setboosttitle [message]\``)
      if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
      const text = args.slice(1).join(" ");
if (!text || text.length > 1024) return message.reply({embeds: [missingargs]});
if(text === "none") {
  db.delete(`boosttitle_${message.guild.id}`)
  const can = new Discord.MessageEmbed()
  .setColor(`0CFF00`)
  .setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted title from the boost message`)
  message.reply({embeds: [can]});
} else {
db.set(`boosttitle_${message.guild.id}`, text)
let mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?user`?/g, message.author.username)
const can = new Discord.MessageEmbed()
.setColor(`0CFF00`)
.setDescription(`<:approve:1006150867029864588>   ${message.author}: Now in boost message title will be \n ${mes} `)
message.reply({embeds: [can]});
     }
    }
    if(message.content.toLowerCase().startsWith(`${prefix}setboostdescription`)) {
      var args = message.content.substring().split(" ");
      const missingperms = new Discord.MessageEmbed()
      .setColor(`FFF300`)
      .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
      const missingargs = new Discord.MessageEmbed()
      .setTitle(`Missing arguments!`)
      .setColor(`FF0000`)
      .setDescription(`\`${prefix}setboostdescription [message]\``)
      if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
      const text = args.slice(1).join(" ");
if (!text || text.length > 1024) return message.reply({embeds: [missingargs]});
db.set(`boostdesc_${message.guild.id}`, text)
let mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?mention`?/g, `${message.author}`).replace(/`?\?boostscount`?/g, `${message.guild.premiumSubscriptionCount}`)
const can = new Discord.MessageEmbed()
.setColor(`0CFF00`)
.setDescription(`<:approve:1006150867029864588>   ${message.author}: Now in boost message description will be \n \`${mes}\` `)
message.reply({embeds: [can]});
    }
    if(message.content.toLowerCase().startsWith(`${prefix}setboostcolor`)) {
      var args = message.content.substring().split(" ");
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setboostcolor [color name / hex code]\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        const text = args.slice(1).join(" ");
        if (!text || text.length > 6) return message.reply({embeds: [missingargs]});
        let upe = text.toUpperCase()
        db.set(`boostcolor_${message.guild.id}`, upe)
        const can = new Discord.MessageEmbed()
        .setColor(`0CFF00`)
        .setDescription(`<:approve:1006150867029864588>   ${message.author}: Color set as ${upe}`)
        message.reply({embeds: [can]});
    }
    if(message.content.toLowerCase().startsWith(`${prefix}setboostfooter`)) {
      var args = message.content.substring().split(" ");
        const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        const missingargs = new Discord.MessageEmbed()
        .setTitle(`Missing arguments!`)
        .setColor(`FF0000`)
        .setDescription(`\`${prefix}setboostfooter [message]\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        const text = args.slice(1).join(" ");
  if (!text || text.length > 1024) return message.reply({embeds: [missingargs]});
  if(text === "none") {
    db.delete(`boostfooter_${message.guild.id}`)
    const can = new Discord.MessageEmbed()
.setColor(`0CFF00`)
.setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted footer from boost message embed`)
message.reply({embeds: [can]});
  } else {
    db.set(`boostfooter_${message.guild.id}`, text)
    let mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?boostscount`?/g, message.guild.premiumSubscriptionCount)
  const can = new Discord.MessageEmbed()
  .setColor(`0CFF00`)
  .setDescription(`<:approve:1006150867029864588>   ${message.author}: Now in boost message footer will be \n \`${mes}\` `)
  message.reply({embeds: [can]});
    }
  }
  if(message.content.toLowerCase().startsWith(`${prefix}setboostthumbnail`)) {
    var args = message.content.substring().split(" ");
    const missingperms = new Discord.MessageEmbed()
    .setColor(`FFF300`)
    .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
    const missingargs = new Discord.MessageEmbed()
    .setTitle(`Missing arguments!`)
    .setColor(`FF0000`)
    .setDescription(`\`${prefix}setboostthumbnail [image link / variable]\`\n\`?useravatar\ to display user avatar or \`?serveravatar\` to display server avatar in thumbnail`)
    if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
    const text = args.slice(1).join(" ");
if (!text || text.length > 1000) return message.reply({embeds: [missingargs]});
if(text === "none") {
db.delete(`boostthumbnail_${message.guild.id}`)
const can = new Discord.MessageEmbed()
.setColor(`0CFF00`)
.setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted thumbnail from boost message embed`)
message.reply({embeds: [can]});
} else {
db.set(`boostthumbnail_${message.guild.id}`, text)
let mes = text.replace(/`?\?useravatar`?/g, message.author.displayAvatarURL({ dynamic: true })).replace(/`?\?serveravatar`?/g, message.guild.iconURL({ dynamic: true}))
message.channel.send(`Now boost thumbnail will be \n \`${mes}\` `)
}
  }
  if(message.content.toLowerCase().startsWith(`${prefix}setboostimage`)) {
    var args = message.content.substring().split(" ");
    const missingperms = new Discord.MessageEmbed()
    .setColor(`FFF300`)
    .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
    const missingargs = new Discord.MessageEmbed()
    .setTitle(`Missing arguments!`)
    .setColor(`FF0000`)
    .setDescription(`\`${prefix}setboostimage [image link]\``)
    if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
    const text = args.slice(1).join(" ");
if (!text || text.length > 1000) return message.reply({embeds: [missingargs]});
if(text === "none") {
db.delete(`boostimage_${message.guild.id}`)
const can = new Discord.MessageEmbed()
.setColor(`0CFF00`)
.setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted image from boost message embed`)
message.reply({embeds: [can]});
} else {
db.set(`boostimage_${message.guild.id}`, text)
message.channel.send(`Now boost image will be \n \`${text}\` `)
}
  }
  if(message.content.toLowerCase().startsWith(`${prefix}deleteboost`) || message.content.toLowerCase().startsWith(`${prefix}delboost`)) {
    const missingperms = new Discord.MessageEmbed()
    .setColor(`FFF300`)
    .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
    if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
    db.delete(`boostchannel_${message.guild.id}`);
    db.delete(`boostdesc_${message.guild.id}`)
    db.delete(`boostimage_${message.guild.id}`)
    db.delete(`boostthumbnail_${message.guild.id}`)
    db.delete(`boostcolor_${message.guild.id}`)
    db.delete(`boosttitle_${message.guild.id}`)
    db.delete(`boostfooter_${message.guild.id}`)
    const can = new Discord.MessageEmbed()
    .setColor(`0CFF00`)
    .setDescription(`<:approve:1006150867029864588>   ${message.author}: Deleted the boost message`)
    message.reply({embeds: [can]});
  }
  if(message.content.toLowerCase().startsWith(`${prefix}testboost`)) {
    const missingperms = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
        if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
        let chreq = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author} channel isn't configuFF0000`)
        let desreq = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`v   ${message.author} description isn't configuFF0000`)
        let channel = db.fetch(`boostchannel_${message.guild.id}`);
        let text = db.fetch(`boostdesc_${message.guild.id}`)
        let img = db.fetch(`boostimage_${message.guild.id}`)
        let nail = db.fetch(`boostthumbnail_${message.guild.id}`)
        let col = db.fetch(`boostcolor_${message.guild.id}`)
        let tit = db.fetch(`boosttitle_${message.guild.id}`)
        let fot = db.fetch(`boostfooter_${message.guild.id}`)
        let titlol
        let tnail
        let mes
        let foter
    if (!channel) message.reply({ embeds: [chreq]});
        if(!col) col = "RANDOM"
        if(tit) titlol = tit.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag)
        if(!tit) titlol = " "
        if(!text) return message.reply({embeds: [desreq]});
        if(text) mes = text.replace(/`?\?user`?/g, message.author.username).replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?mention`?/g, `${message.author}`).replace(/`?\?boostscount`?/g, `${message.guild.premiumSubscriptionCount}`);
        if(!fot) foter = " "
        if(fot) foter = fot.replace(/`?\?server`?/g, message.guild.name).replace(/`?\?tag`?/g, message.author.tag).replace(/`?\?boostscount`?/g, message.guild.premiumSubscriptionCount)
if(nail) tnail = nail.replace(/`?\?useravatar`?/g, message.author.displayAvatarURL({ dynamic: true })).replace(/`?\?serveravatar`?/g, message.guild.iconURL({ dynamic: true }))
if(!nail) tnail = " "
 const embedboost = new Discord.MessageEmbed()
.setTitle(`${titlol}`)
   .setDescription(`${mes}`)
   .setColor(`${col}`)
   .setImage(img)
   .setThumbnail(`${tnail}`)
   .setFooter(`${foter}`)
    client.channels.cache.get(channel).send({ embeds: [embedboost]})
  }
  if(message.content.toLowerCase() === (`${prefix}boost variables`)) {
    const missingperms = new Discord.MessageEmbed()
    .setColor(`FFF300`)
    .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_server\``)
    if (! message.member.permissions.has("MANAGE_GUILD")) return message.reply({embeds: [missingperms]});
    let variables = new Discord.MessageEmbed()
    .setAuthor(message.author.tag, message.author.displayAvatarURL({ dynamic: true }))
    .setColor(`BLACK`)
    .setTitle(`Boost message variables`)
    .setDescription(`?server - shows server name 
?tag shows member's full name - wintrs#2000
?mention - mentions new user - @wintrs
?user - shows new user username - wintrs
?useravatar - shows user's avatar
?serveravatar - shows server's avatar
?boostscount - shows number of boosts from the server - 10 boosts
`)
message.reply({embeds: [variables]});  }
  if(message.content.toLowerCase() === `${prefix}help boost`) {
    const helpwelcome = new Discord.MessageEmbed()
    .setAuthor(message.author.tag, message.author.displayAvatarURL({ dynamic: true }))
    .setTitle(`Boost message setup help`)
    .setColor(`BLACK`)
    .addField(`Boost embed commands`, `${prefix}setboostchannel - sets boost channel (requieFF0000)\n${prefix}setboosttitle - sets boost message title\n${prefix}setboostcolor - sets boost message color (can be an hex code or color name only, otherwise this module might have errors)\n${prefix}setboostdescription - sets boost description (requieFF0000)\n${prefix}setboostthumbnail - sets boost messsage thumbnail\n${prefix}setboostimage - sets boost message image\n${prefix}setboostfooter - sets boost message footer\n${prefix}testboost - sends boost message`)
    .addField(`Welcome variables`, `?server - shows server name 
?tag shows member's full name - wintrs#2000
?mention - mentions new user - @wintrs
?user - shows new user username - wintrs
?useravatar - shows user's avatar
?serveravatar - shows server's avatar
?boostscount - shows number of boosts from the server - 10 boosts`)
    message.reply({embeds: [helpwelcome]});
  }
       /*


       ADD EMOJI


       */
  if(message.content.startsWith(`${prefix}imgaddemoji`)) {
    let missingperms = new Discord.MessageEmbed()
    .setColor(`FFF300`)
    .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_emojis\``)

    let botperms = new Discord.MessageEmbed()
    .setColor(`FFF300`)
    .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`manage_emojis\``)

    const bruhlol = new Discord.MessageEmbed()
    .setColor(`FF0000`)
    .setDescription(`<:deny:999025481183662110> Unable to add the emoji. Make sure the image format is either png or gif and there are enough emoji slots in your server`)

    const missingargs = new Discord.MessageEmbed()
    .setTitle(`Missing arguments!`)
    .setColor(`FF0000`)
    .setDescription(`\`${prefix}imgaddemoji [image link] [emoji name]\``)
    if(! message.member.permissions.has('MANAGE_EMOJIS')) return message.reply({embeds: [missingperms]});
    if(!message.guild.me.permissions.has('MANAGE_EMOJIS')) return message.reply(botperms)
    var params = message.content.substring().split(" ");
    params[0] = params[0].toLowerCase();
    let emoji = params[1]
    let name = params.slice(2).join(' ')
    if(!emoji) return message.reply({embeds: [missingargs]});
    if(!name) return message.reply({embeds: [missingargs]});
    message.guild.emojis.create(emoji, name)
            .then(emoji => message.channel.send(`${emoji} Created new emoji with name \`${emoji.name}\``))
            .catch(error => {
              message.channel.send({embeds: [bruhlol]})
            })
  }
  if(message.content.startsWith(`${prefix}emoji`)) {
    let missingperms = new Discord.MessageEmbed()
    .setColor(`FFF300`)
    .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_emojis\``)

    let botmissingperms = new Discord.MessageEmbed()
    .setColor(`FFF300`)
    .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`manage_emojis\``)

    let missingargs = new Discord.MessageEmbed()
    .setTitle(`Missing arguments!`)
    .setColor(`FF0000`)
      .setDescription(`\`${prefix}emoji [emoji] [name (optional)]\``)

    let failed = new Discord.MessageEmbed()
    .setColor(`FF0000`)
    .setDescription(`<:deny:999025481183662110> Failed to add emoji`)
    if(! message.member.permissions.has('MANAGE_EMOJIS')) return message.reply({embeds: [missingperms]});
    if(!message.guild.me.permissions.has('MANAGE_EMOJIS')) return message.reply({embeds: [botmissingperms]});
    args = message.content.substring().split(" ");
    let emojis = args[1]
    if(!emojis) return message.reply({embeds: [missingargs]});
    const getEmoji = Discord.Util.parseEmoji(emojis);
    if(getEmoji.id) 
    {
      const emojiExt = getEmoji.animated ? ".gif" : ".png";
      let name = args.slice(2).join(' ')
      if(!name) name = getEmoji.name
      const emojiURL = `https://cdn.discordapp.com/emojis/${getEmoji.id + emojiExt}`
      message.guild.emojis.create(emojiURL, name)
      .then(emoji => message.reply(`${emoji} Created new emoji with name \`${name}\``))
      .catch(error => message.reply(failed))
    }
  }
  if(message.content.startsWith(`${prefix}addmultiple`)) {
    let missingperms = new Discord.MessageEmbed()
    .setColor(`FFF300`)
    .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're **missing** permissions \`manage_emojis\``)

    let botmissingperms = new Discord.MessageEmbed()
    .setColor(`FFF300`)
    .setDescription(`<:warn:1006150861195587604>    ${client.user} is **missing** permissions \`manage_emojis\``)

    let missingargs = new Discord.MessageEmbed()
    .setTitle(`Missing arguments!`)
    .setColor(`FF0000`)
    .setDescription(`\`${prefix}addemultiple [emojis]\``)

    let failed = new Discord.MessageEmbed()
    .setColor(`FF0000`)
    .setDescription(`<<:deny:999025481183662110> Failed to add emoji`)
    if(! message.member.permissions.has('MANAGE_EMOJIS')) return message.reply({embeds: [missingperms]});
    if(!message.guild.me.permissions.has('MANAGE_EMOJIS')) return message.reply({embeds: [botmissingperms]});

    args = message.content.substring().split(" ")
    if(!args.length) {
       message.reply({embeds: [missingargs]});
    } else {
    for (const emojis of args) {
    const getEmoji = Discord.Util.parseEmoji(emojis)

    if(getEmoji.id) {
      const emojiExt = getEmoji.animated ? ".gif" : ".png"
      const emojiURL = `https://cdn.discordapp.com/emojis/${getEmoji.id + emojiExt}`
      message.guild.emojis
      .create(emojiURL, getEmoji.name)
      .then(emoji => message.channel.send(`${emoji} Created new emoji with name \`${emoji.name}\``))
      .catch(error => message.channel.send(failed))
    }
  }
    }
  }
  if(message.content.startsWith(`${prefix}downloademoji`)) {
    const missingargs = new Discord.MessageEmbed()
    .setTitle(`Missing arguments!`)
    .setColor(`FF0000`)
    .setDescription(`\`${prefix}download emoji [emoji]\``)
    var params = message.content.substring().split(" ");
    params[0] = params[0].toLowerCase();
    let emoji = params[1]
    const getEmoji = Discord.Util.parseEmoji(emoji)
    if(!emoji) return message.reply({embeds: [missingargs]});
    if(getEmoji.id) {
      const emojiExt = getEmoji.animated ? ".gif" : ".png"
      const emojiURL = `https://cdn.discordapp.com/emojis/${getEmoji.id + emojiExt}`
      const emojisend = new Discord.MessageEmbed()
      .setTitle(`Here is your emoji`)
      .setColor(`BLACK`)
      .setImage(emojiURL)
      .setFooter(`Requested by ${message.author.username}`, message.author.displayAvatarURL({
        dynamic: true
      }))
      .setTimestamp()
      message.reply(emojisend)
    }
  }
  if(message.content === `${prefix}emojilist`) {
    const charactersPerMessage = 2000;
    const emojis = message.guild.emojis.cache
 .map((e) => `${e}`)
 .join(' ');
    const numberOfMessages = Math.ceil(emojis.length / charactersPerMessage);
    const embed = new Discord.MessageEmbed()
    .setTitle(`Emoji list in ${message.guild.name}!`)
    .setColor(`BLACK`)
    .setThumbnail(message.guild.iconURL({ dynamic: true}))
    for (i = 0; i < numberOfMessages; i++) {
      embed.setDescription(emojis.slice(i * charactersPerMessage, (i + 1) * charactersPerMessage))
      message.channel.send({embeds: [embed]})  
    }
  }
  /*


  SET NICKNAME


  */
        if(message.content.startsWith(`${prefix}setnick`) || message.content.startsWith(`${prefix}setnickname`)) {
          const missingperms = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>   ${message.author}: You're **missing** permissions \`manage_nicknames\``)

          const missingargs = new Discord.MessageEmbed()
          .setTitle(`Missing arguments!`)
          .setColor(`FF0000`)
          .setDescription(`\`${prefix}setnickname [user mention / user id] [nickname]\`
Aliases: \`setnick\``)

const hieracy = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>   ${message.author}: You cannot set a nickname to someone with an equal or higher role`)

          const hieracy2 = new Discord.MessageEmbed()
          .setColor(`FF0000`)
          .setDescription(`<:deny:999025481183662110> i couldn't set the nickname to this member`)
          if(! message.member.permissions.has(`MANAGE_NICKNAMES`)) return message.reply({embeds: [missingperms]});
          if(!message.guild.me.permissions.has(`MANAGE_NICKNAMES`)) return message.reply({embeds: [missingperms]});
          var params = message.content.substring().split(" ");
                    params[0] = params[0].toLowerCase();
          const user = message.mentions.members.first() || message.guild.members.cache.get(params[1])
          if(!user) return message.reply({embeds: [missingargs]});
          if(user.roles.highest.position >= message.member.roles.highest.position && message.author.id !== message.guild.owner.id && message.author.id !== user.id) return message.channel.send(hieracy)
          if(user.roles.highest.position >= message.guild.me.roles.highest.position) return message.channel.send(hieracy2)
          var newNickname = params.slice(2).join(' ');
          user.setNickname(newNickname).catch(err => {
            console.log(`error`)
          })
          if(!newNickname) {
            let changed = new Discord.MessageEmbed()
            .setColor(`0CFF00`)
            .setDescription(`<:approve:1006150867029864588>    deleted ${user.user.tag}'s nickname`)
            message.reply(changed)
          } else {
            let deleted = new Discord.MessageEmbed()
            .setColor(`0CFF00`)
            .setDescription(`<:approve:1006150867029864588>    changed \`${user.user.tag}'s\` nickname to \`${newNickname}\``)
          message.reply(deleted)
          }
        }
        if(message.content.startsWith(`${prefix}setbotnick`) || message.content.startsWith(`${prefix}setbotnickname`)) {
          const missingperms = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>   ${message.author}: You're **missing** permissions \`manage_nicknames\``)

          const botmissingperms = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>   ${client.user} is **missing** permissions \`change_nickname\``)
          if(! message.member.permissions.has('MANAGE_NICKNAMES') && message.author.id !== south) return message.reply({embeds: [missingperms]});
          if(!message.guild.me.permissions.has('CHANGE_NICKNAME')) return message.reply({embeds: [botmissingperms]});
          var params = message.content.substring().split(" ");
          params[0] = params[0].toLowerCase();
          var botNickname = params.slice(1).join(' ');
          message.guild.me.setNickname(botNickname).catch(console.error)
          if(!botNickname) {
            let deleted = new Discord.MessageEmbed()
            .setColor(`0CFF00`)
            .setDescription(`<:approve:1006150867029864588>     removed sychol's nickname`)
            message.reply(deleted)
          } else {
            let changed = new Discord.MessageEmbed()
            .setColor(`0CFF00`)
            .setDescription(`<:approve:1006150867029864588>     changed sychol's nickname to ${botNickname}`)
          message.reply(changed)
          }
        } 
        /*


        TRANSLATE


        */
        if(message.content.startsWith(`${prefix}translate`)) {
          args = message.content.split(" ").slice(1);
         const query = args.slice(1).join(' ')
         const notext = new MessageEmbed()
         .setAuthor(`${client.user.username} help`, client.user.displayAvatarURL())
         .setTitle(`Command: translate`)
         .setColor(`BLACK`)
         .setDescription(`Translates text\n\`\`\`Syntax: translate (language) <text>\nExample: ${prefix}translate en bonjour\`\`\`\nsupported languages: af, sq, am, ar, hy, az, eu, be, bn, bs, bg, ca, ceb, ny, zh-CN, zh-TW, co, hr, cs, da, nl, en, eo, et, tl, fi, fr, fy, gl, ka, de, el, gu, ht, ha, haw, he, iw, hi, hmn, hu, is, ig, id, ga, it, ja, jw, kn, kk, km, ko, ku, ky, lo, la, lv, lt, lb, mk, mg, ms, ml, mt, mi, mr, mn, my, ne, no, ps, fa, pl, pt, pa, ro, ru, sm, gd, sr, st, sn, sd, si, sk, sl, so, es, su, sw, sv, tg, ta, te, th, tr, uk, ur, uz, vi, cy, xh, yi, yo, zu`)
         if (!query) return message.reply(notext)
      
         const arg = args[0]
      
         const translated = await translate(query, { to: `${arg}`}).catch(error => {
          message.reply(`unsupported language, it has to be one of the following: af, sq, am, ar, hy, az, eu, be, bn, bs, bg, ca, ceb, ny, zh-CN, zh-TW, co, hr, cs, da, nl, en, eo, et, tl, fi, fr, fy, gl, ka, de, el, gu, ht, ha, haw, he, iw, hi, hmn, hu, is, ig, id, ga, it, ja, jw, kn, kk, km, ko, ku, ky, lo, la, lv, lt, lb, mk, mg, ms, ml, mt, mi, mr, mn, my, ne, no, ps, fa, pl, pt, pa, ro, ru, sm, gd, sr, st, sn, sd, si, sk, sl, so, es, su, sw, sv, tg, ta, te, th, tr, uk, ur, uz, vi, cy, xh, yi, yo, zu`)
         })
         const embed = new MessageEmbed()
         .setTitle(`Translated to ${arg}`)
         .setColor('BLACK')
         .setDescription(`\`\`\`${translated.text}\`\`\``)   
         message.channel.send({embeds: [embed]}).catch (error => {
          console.log(`error`)
        })
      }
      if(message.content.startsWith(`${prefix}search`)) {
        args = message.content.split(" ").slice(1);
        const embed = new Discord.MessageEmbed()
        .setTitle("Search Results")
        .setColor(`BLACK`)
        .setTimestamp()
    googleIt({'query': args.join(' ')}).then(results => {
        results.forEach(function(item, index) { 
            embed.addField((index + 1) + ": " + item.title, "<" + item.link + ">");
        });
       message.reply({embeds: [embed]});;
    }).catch(e => {
        console.log(`error`)
    });
      }
      /*


      NSFW


      */
        if (message.content === (`${prefix}nsfw 4k`)) {
          const nonnsfw = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're not allowed to use **nsfw** commands here`)
          if (!message.channel.nsfw) return message.reply(nonnsfw)
            const { image } = await fetch('http://api.nekos.fun:8080/api/4k').then(response => response.json())
            const doneEmbed = new Discord.MessageEmbed()
            .setColor('BLACK')
            .setTitle('Here is some 4k nsfw')
            .setImage(image)
            message.reply(doneEmbed);
        
      }
      if (message.content === (`${prefix}nsfw cum`)) {
        const nonnsfw = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're not allowed to use **nsfw** commands here`)
          if (!message.channel.nsfw) return message.reply(nonnsfw)
            const { image } = await fetch('http://api.nekos.fun:8080/api/cum').then(response => response.json())
            const doneEmbed = new Discord.MessageEmbed()
            .setColor('BLACK')
            .setTitle('Here is some cum nsfw')
            .setImage(image)
            message.reply(doneEmbed);
      }
      if (message.content === (`${prefix}nsfw boobs`)) {
        const nonnsfw = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're not allowed to use **nsfw** commands here`)
          if (!message.channel.nsfw) return message.reply(nonnsfw)
            const { image } = await fetch('http://api.nekos.fun:8080/api/boobs').then(response => response.json())
            const doneEmbed = new Discord.MessageEmbed()
            .setColor('BLACK')
            .setTitle('Here are some boobs')
            .setImage(image)
            message.reply(doneEmbed);
      }
      if (message.content===(`${prefix}nsfw spank`)) {
        const nonnsfw = new Discord.MessageEmbed()
          .setColor(`FFF300`)
          .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're not allowed to use **nsfw** commands here`)
          if (!message.channel.nsfw) return message.reply(nonnsfw)
            const { image } = await fetch('http://api.nekos.fun:8080/api/spank').then(response => response.json())
            const doneEmbed = new Discord.MessageEmbed()
            .setColor('BLACK')
            .setTitle('Spanking')
            .setImage(image)
            message.reply(doneEmbed);
      }
      if (message.content===(`${prefix}nsfw lesbian`)) {
        const nonnsfw = new Discord.MessageEmbed()
        .setColor(`FFF300`)
        .setDescription(`<:warn:1006150861195587604>    ${message.author}: You're not allowed to use **nsfw** commands here`)
          if (!message.channel.nsfw) return message.reply(nonnsfw)
            const { image } = await fetch('http://api.nekos.fun:8080/api/lesbian').then(response => response.json())
            const doneEmbed = new Discord.MessageEmbed()
            .setColor('BLACK')
            .setTitle('Here are some lesbians')
            .setImage(image)
            message.reply(doneEmbed);
      }
if(message.content.startsWith(`${prefix}nsfw`)) {
  args = message.content.split(" ").slice(1);
const answer = args.join(" ")
const nonnsfw = new Discord.MessageEmbed()
.setColor(`FFF300`)
.setDescription(`<:warn:1006150861195587604>    ${message.author}: You're not allowed to use **nsfw** commands here`)
if (!message.channel.nsfw) {
  message.channel.send(nonnsfw) 
} else if (answer == 'ass') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.ass())
    message.channel.send({embeds: [embed]})
} else if (answer == 'bdsm') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.bdsm())
    message.channel.send({embeds: [embed]})
} else if (answer == 'blowjob') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.blowjob())
    message.channel.send({embeds: [embed]})
} else if (answer == 'blowjob') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.blowjob())
    message.channel.send({embeds: [embed]})
} else if (answer == 'doujin') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.doujin())
    message.channel.send({embeds: [embed]})
} else if (answer == 'feet') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.feet())
    message.channel.send({embeds: [embed]})
} else if (answer == 'femdom') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.femdom())
    message.channel.send({embeds: [embed]})
} else if (answer == 'foxgirl') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.foxgirl())
    message.channel.send({embeds: [embed]})
} else if (answer == 'gifs') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.gifs())
    message.channel.send({embeds: [embed]})
} else if (answer == 'glasses') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.glasses())
    message.channel.send({embeds: [embed]})
} else if (answer == 'hentai') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.hentai())
    message.channel.send({embeds: [embed]})
} else if (answer == 'netorare') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.netorare())
    message.channel.send({embeds: [embed]})
} else if (answer == 'maid') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.maid())
    message.channel.send({embeds: [embed]})
} else if (answer == 'masturbation') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.masturbation())
    message.channel.send({embeds: [embed]})
} else if (answer == 'orgy') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.orgy())
    message.channel.send({embeds: [embed]})
} else if (answer == 'panties') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.panties())
    message.channel.send({embeds: [embed]})
} else if (answer == 'pussy') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.pussy())
    message.channel.send({embeds: [embed]})
} else if (answer == 'school') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.school())
    message.channel.send({embeds: [embed]})
} else if (answer == 'succubus') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.succubus())
    message.channel.send({embeds: [embed]})
} else if (answer == 'tentacles') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.tentacles())
    message.channel.send({embeds: [embed]})
} else if (answer == 'thighs') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.thighs())
    message.channel.send({embeds: [embed]})
} else if (answer == 'uglyBastard') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.uglyBastard())
    message.channel.send({embeds: [embed]})
} else if (answer == 'uniform') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.uniform())
    message.channel.send({embeds: [embed]})
} else if (answer == 'yuri') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.yuri())
    message.channel.send({embeds: [embed]})
} else if (answer == 'zettaiRyouiki') {
    const embed = new Discord.MessageEmbed()
        .setImage(await akaneko.nsfw.zettaiRyouiki())
    message.channel.send({embeds: [embed]})
} else if (!answer || !message.content === `${prefix}nsfw help`) {
  const blank = new Discord.MessageEmbed()
      .setColor('FF0000')
      .setTitle('Missing arguments!')
      .setDescription(`${prefix}nsfw [nsfw command]`)
      .setTimestamp()
      .setFooter('Nsfw command.');

  message.channel.send(blank)
}
}
/*


BOT GUILDS


*/
 if(message.content === `${prefix}guildcount`) {
   let counter = new Discord.MessageEmbed()
   .setTitle(`${client.user.username} guild count`)
   .setColor(`BLACK`)
     .setDescription(`> **${client.user.username} is in ${client.guilds.cache.size} guilds**`)
   .setTimestamp()
   message.reply({embeds: [counter]})
 }
 if(message.content.startsWith(`${prefix}leaveguild`)) {
   const noguilds = new Discord.MessageEmbed()
   .setTitle(`Guild id not found!`)
   .setColor(`BLACK`)
   .setDescription(`\`${prefix}leaveguild [guild id]\``)
   if (message.author.id !=='605366345902587921') 
        return
        args = message.content.split(" ").slice(1);
    var guildID = client.guilds.cache.get(args[0]) 
   if (!guildID) return message.channel.send({ embeds: [noguilds] })
    guildID.leave()
    message.channel.send(`Left ${guildID.name} 👍`)
 }



 if (message.content.startsWith(`${prefix}guilds`)) {    
   const ownerid = "605366345902587921";



   

       if (message.author.id !== ownerid) return message.reply(new Discord.MessageEmbed().setDescription('**<:icons_Wrong:1012407246627557456>  Insufficient permissions you need to be the bot owner** ').setColor('FF0000'))
       if (message.author.id == ownerid) {
         if (!message.guild.me.permissions.has("EMBED_LINKS"))
           return message.channel
             .send("i don't have permissions to send embeds lol")
             .then(msg => msg.delete({ timeout: 5000 }));

         let i0 = 0;
         let i1 = 10;
         let page = 1;

         let description =
           `Total Servers - ${client.guilds.cache.size}\n\n` +
           client.guilds.cache
             .sort((a, b) => b.memberCount - a.memberCount)
             .map(r => r)
             .map((r, i) => `**${i + 1}** - ${r.name} | ${r.memberCount} Members\nID - ${r.id}`)
             .slice(0, 10)
             .join("\n\n");

         let embed = new Discord.MessageEmbed()
           .setAuthor(client.user.tag, client.user.displayAvatarURL({ dynamic: true }))

           .setColor('BLACK')
           .setFooter(`Page - ${page}/${Math.ceil(client.guilds.cache.size / 10)}`)
           .setDescription(description);

         let msg = await message.channel.send({embeds: [embed]});

         await msg.react("⬅");
         await msg.react("⏹️");
         await msg.react("➡");

         let collector = msg.createReactionCollector(
           (reaction, user) => user.id === message.author.id
         );

         collector.on("collect", async (reaction, user) => {
           if (reaction._emoji.name === "⬅") {
             i0 = i0 - 10;
             i1 = i1 - 10;
             page = page - 1;

             if (i0 + 1 < 0) {
               console.log(i0)
               return msg.delete();
             }
             if (!i0 || !i1) {
               return msg.delete();
             }

             description =
               `Total Servers - ${client.guilds.cache.size}\n\n` +
               client.guilds.cache
                 .sort((a, b) => b.memberCount - a.memberCount)
                 .map(r => r)
                 .map(
                   (r, i) => `**${i + 1}** - ${r.name} | ${r.memberCount} Members\nID - ${r.id}`)
                 .slice(i0, i1)
                 .join("\n\n");

             embed
               .setFooter(
                 `Page - ${page}/${Math.round(client.guilds.cache.size / 10 + 1)}`
               )
               .setDescription(description);

             msg.edit({ embeds: [embed] });
           }

           if (reaction._emoji.name === "➡") {
             i0 = i0 + 10;
             i1 = i1 + 10;
             page = page + 1;

             if (i1 > client.guilds.cache.size + 10) {
               return msg.delete();
             }
             if (!i0 || !i1) {
               return msg.delete();
             }

             description =
               `Total Servers - ${client.guilds.cache.size}\n\n` +
               client.guilds.cache
                 .sort((a, b) => b.memberCount - a.memberCount)
                 .map(r => r)
                 .map(
                   (r, i) => `**${i + 1}** - ${r.name} | ${r.memberCount} Members\nID - ${r.id}`)
                 .slice(i0, i1)
                 .join("\n\n");

             embed
               .setFooter(
                 `Page - ${page}/${Math.round(client.guilds.cache.size / 10 + 1)}`
               )
               .setDescription(description);

             msg.edit({embeds: [embed]});
           }

           if (reaction._emoji.name === "⏹️") {
             return msg.delete();
           }

           await reaction.users.remove(message.author.id);
         });
       } else {
         return;
       }
     }
    }

)
const { webhookId, webhookToken } = require('./config.json');
const wrb = new WebhookClient({ id: webhookId, token: webhookToken });

client.on("guildCreate", async(guild) => {
   const joinguild = new Discord.MessageEmbed()
   .setTitle(`<:approve:1018877503634415718>     Joined a guild`)
   .setColor(`BLACK`)
   .setDescription(`Joined ${guild.name}`)
   .setThumbnail(guild.iconURL({ dynamic: true}))
     .addFields(
       { name: 'Membercount', value: `\`\`\`${guild.memberCount}\`\`\`` },
       { name: 'Guild Name', value: `\`\`\`${guild.name}\`\`\``, inline: true },

     ).setFooter(`${guild.id}`)
   .setTimestamp()
  await wrb.send({
    content: 'Joined a guild',
    username: 'raid',
    avatarURL: 'https://cdn.discordapp.com/avatars/1017895318664265728/3fd07ccbb416816c89b48706aa78b3f3.webp?size=1024',
    embeds: [joinguild],

  })
})


  client.on("guildDelete", async(guild) => {
const owner2 = await guild.fetchOwner()
  const leaveguild = new Discord.MessageEmbed()
  .setTitle(`<:deny:1018877590599127162>  Left a guild`)
  .setColor(`BLACK`)
  .setDescription(`Left ${guild.name}`)
  .setThumbnail(guild.iconURL({ dynamic: true}))
    .addFields(
      { name: 'Membercount', value: `\`\`\`${guild.memberCount}\`\`\`` },
      { name: 'Guild Name', value: `\`\`\`${guild.name}\`\`\``, inline: true },

    )   .setFooter(`${guild.id}`)
  .setTimestamp()
  await wrb.send({
    content: 'Left a guild',
    username: 'raid',
    avatarURL: 'https://cdn.discordapp.com/avatars/1017895318664265728/3fd07ccbb416816c89b48706aa78b3f3.webp?size=1024',
    embeds: [leaveguild],

})

}) //https://discord.com/api/webhooks/958745251265273968/yjtEtZcnQiuwEHp9E-rc9Q4gVRhrKn6XxKLIuhO8Pzm93w6zh98DY-ukyP7azUUu-Lcx
client.login(token.TOKEN);