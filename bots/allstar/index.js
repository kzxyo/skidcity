const fs = require("fs");
const database = require('quick.db')
const db = require('quick.db')
const { Client, Intents, Collection, MessageEmbed, Permissions, GatewayIntentBits, MessageAttachment, MessageActionRow, MessageButton } = require("discord.js");
const axios = require('axios')
const request = require('request');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');
const client = new Client({
  intents: [
    Intents.FLAGS.GUILDS,
    Intents.FLAGS.GUILD_MEMBERS,
    Intents.FLAGS.GUILD_BANS,
    Intents.FLAGS.GUILD_EMOJIS_AND_STICKERS,
    Intents.FLAGS.GUILD_INTEGRATIONS,
    Intents.FLAGS.GUILD_WEBHOOKS,
    Intents.FLAGS.GUILD_INVITES,
    Intents.FLAGS.GUILD_PRESENCES,
    Intents.FLAGS.GUILD_VOICE_STATES,
    Intents.FLAGS.GUILD_MESSAGES,
    Intents.FLAGS.GUILD_MESSAGE_REACTIONS,
    Intents.FLAGS.GUILD_MESSAGE_TYPING,
    Intents.FLAGS.DIRECT_MESSAGES,
    Intents.FLAGS.DIRECT_MESSAGE_REACTIONS,
    Intents.FLAGS.DIRECT_MESSAGE_TYPING,
  ],
  ws: { properties: { $browser: "Discord iOS" } },
  restTimeOffset: 0,
  allowedMentions: {
    parse: ["roles", "users"],
    repliedUser: false,
  }
});

const mariadb = require('mariadb');
global.db =  mariadb.createPool({
   host :  "localhost",
   user : "luisu",
   password : "Luis6672$",
   connectionLimit: 5

})
const { QuickDB, MySQLDriver } = require('quick.db');
(async () => {
  const mysql = new MySQLDriver({
    host:     'localhost',
    user:     'luisu',
    password: 'Luis6672$',
    database: 'allstar'
  });
  
  await mysql.connect();

  
   client.db = new QuickDB({ driver: mysql });
})();

client.slash_data = []
client.slash = new Collection();
const slashFiles = fs.readdirSync('./slash-cmd').filter(file => file.endsWith('.js'));
for (const file of slashFiles) {
	const command = require(`./slash-cmd/${file}`);
	client.slash_data.push(command.slashCmd.toJSON());
  client.slash.set(command.slashCmd.name, command);
}

const { token, default_prefix, color, error } = require("./config.json");

const rest = new REST({ version: '9' }).setToken(token);

(async () => {
	try {
		console.log(`Slash Commands: Started Registration Of ${client.slash_data.length} Slash Command(s).`);

		 await rest.put(
			Routes.applicationGuildCommands("938863295543251024", "1031650118375571537"),
			{ body: client.slash_data },
		);
     await rest.put(
			Routes.applicationGuildCommands("938863295543251024", "981558759115591690"),
			{ body: client.slash_data },
		); 

		console.log(`Slash Commands: Registered ${client.slash_data.length} Slash Command(s).`);
	} catch (error) {
		console.error(error)
	}
})();

client.loadedOn = Date.now()

client.on('interactionCreate', async (interaction) => {
	require("./handlers/slashCmd.js").runEvent(client, interaction, Date.now())
});

console
global.exec = function (code) { const { execSync } = require("child_process"); return execSync(code.toString()).toString() }
const headers = { "Authorization": 'Bot ' + token };
client.commands = new Collection();
client.aliases = new Collection();

fs.readdir("./commands/", async (err, files) => {
  const commandHandler = require("./handlers/command");
  await commandHandler(err, files, client);
});

fs.readdir("./events/", (err, files) => {
  const eventHandler = require("./handlers/event");
  eventHandler(err, files, client);
});


client.on("guildMemberAdd", async (member) => {
  if (member.user.bot) return;


  const newMember = member
  const role = member.guild.roles.cache.find(r => r.id === db.get(`autorole_${member.guild.id}`));
  if (role) member.roles.add(role, {
    reason: "Auto-Role"
  });


})

const usersMap = new Map();
const LIMIT = 10;
const DIFF = 1500;

client.on('messageCreate', async (message) => {

  try {
    //   if (message.author.id === member.guild.ownerId) return;
    //if (message.author.id === client.user.id) return;
    let trustedusers = db.get(`trustedusers_${message.guild.id}`)
    if (trustedusers && trustedusers.find(find => find.user == message.author.id)) {
      return;
    }


    let member = message.guild.members.cache.get(message.author.id)
    // if(message.author.bot) return;
    const antiRaid = await db.get(`antispam_${message.guild.id}`);
    if (antiRaid !== true) return
    if (message.content.includes("@everyone")) {
      await member.timeout(470000, {
        reason: "Anti Raid"
      });
      await member.roles.cache.map(roled => {
        if (roled.managed) return;
        member.roles.remove(roled)
      })

    }
    if (message.content.includes("@here")) {
      await member.timeout(470000, {
        reason: "Anti Raid"
      });
      await member.roles.cache.map(roled => {
        member.roles.remove(roled)
      })

    }
    if (usersMap.has(message.author.id)) {
      const userData = usersMap.get(message.author.id);
      const { lastMessage, timer } = userData;
      const difference = message.createdTimestamp - lastMessage.createdTimestamp;
      let msgCount = userData.msgCount;


      if (difference > DIFF) {
        clearTimeout(timer);

        userData.msgCount = 1;
        userData.lastMessage = message;
        userData.timer = setTimeout(() => {
          usersMap.delete(message.author.id);
          // console.log('Removed from map.')
        }, 47000);
        usersMap.set(message.author.id, userData)
      }
      else {
        ++msgCount;
        if (parseInt(msgCount) === LIMIT) {

          await member.timeout(470000, {
            reason: "Anti Raid"
          });
          // await member.roles.cache.map(roled => {
          ///  })
          await member.edit({
            roles: '',
          }).catch(() => { })

          message.channel.bulkDelete(LIMIT);

        } else {
          await member.timeout(470000, {
            reason: "Anti Raid"
          });
          await member.roles.cache.map(roled => {
            member.roles.remove(roled).catch(console.log)
          })
          userData.msgCount = msgCount;
          usersMap.set(message.author.id, userData);
        }
      }
    }
    else {
      let fn = setTimeout(() => {

        usersMap.delete(message.author.id);
        //console.log('Removed from map.')
      }, 47000);
      usersMap.set(message.author.id, {
        msgCount: 1,
        lastMessage: message,
        timer: fn
      });
    }
  } catch { }
})
// Anti Alt
const ms = require('moment');
client.on('guildMemberAdd', async (member) => {

  const anti = await db.get(`antiraid_${member.guild.id}`);
  if (anti) {
    let minAge = (1210000000)
    let creD = new Date(member.user.createdAt);
    let notS = Date.now() - creD.getTime();

    if (minAge > notS) {

      member.kick('Anti Alt Account')

    }
  } else return;
});
client.on("guildMemberRemove", async (member) => {
  let chx = db.get(`leavechannel_${member.guild.id}`);
  if (chx === null) {
    return;
  }
  let welcome = db.get(`leavemessage_${member.guild.id}`);
  if (welcome === null) {
    return;
  }
  let footer = db.get(`leaveembed_${member.guild.id}`);
  if (footer === null) { footer = `` }
  let image = db.get(`leaveimage_${member.guild.id}`)
  if (image === null) {
    //image = `https://cdn.discordapp.com/attachments/989999587890712606/990905254138765362/Screenshot_7.png`
  }
  let author = db.get(`leaveauthor_${member.guild.id}`)
  if (author === null) {
    author = ""
  }
  let colors = db.get(`leavecolor_${member.guild.id}`)
  if (colors === null) {
    colors = color;
  }
  let thumbnail = db.get(`leavethumbnail_${member.guild.id}`)
  if (thumbnail === null) {
    thumbnail = ` `
  }
  if (thumbnail === '')

    if (thumbnail) thumbnail = thumbnail.replace('{user.icon}', member.user.displayAvatarURL({ dynamic: true }));
  if (thumbnail) thumbnail = thumbnail.replace('{guild.icon}', member.guild.iconURL({ dynamic: true }));
  if (image) image = image.replace('{user.icon}', member.user.displayAvatarURL({ dynamic: true }));
  if (image) image = image.replace('{guild.icon}', member.guild.iconURL({ dynamic: true }));

  welcome = welcome.replace('{user}', member);
  welcome = welcome.replace('{user.name}', member.user.username);
  welcome = welcome.replace('{user.tag}', member.user.tag);
  welcome = welcome.replace('{user.id}', member.user.id);
  welcome = welcome.replace('{membercount}', member.guild.memberCount);
  const ordinal = (member.guild.memberCount.toString().endsWith(1) && !member.guild.memberCount.toString().endsWith(11)) ? 'st' : (member.guild.memberCount.toString().endsWith(2) && !member.guild.memberCount.toString().endsWith(12)) ? 'nd' : (member.guild.memberCount.toString().endsWith(3) && !member.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
  welcome = welcome.replace('{membercount.ordinal}', member.guild.memberCount + ordinal);
  welcome = welcome.replace('{guild.name}', member.guild.name);
  welcome = welcome.replace('{guild.id}', member.guild.id);

  footer = footer.replace('{user}', member);
  footer = footer.replace('{user.name}', member.user.username);
  footer = footer.replace('{user.tag}', member.user.tag);
  footer = footer.replace('{user.id}', member.user.id);
  footer = footer.replace('{membercount}', member.guild.memberCount);
  footer = footer.replace('{membercount.ordinal}', member.guild.memberCount + ordinal);
  footer = footer.replace('{guild.name}', member.guild.name);
  footer = footer.replace('{guild.id}', member.guild.id);

  author = author.replace('{user}', member);
  author = author.replace('{user.name}', member.user.username);
  author = author.replace('{user.tag}', member.user.tag);
  author = author.replace('{user.id}', member.user.id);
  author = author.replace('{membercount}', member.guild.memberCount);
  author = author.replace('{membercount.ordinal}', member.guild.memberCount + ordinal);
  author = author.replace('{guild.name}', member.guild.name);
  author = author.replace('{guild.id}', member.guild.id);
  if (thumbnail === '{user.icon}') thumbnail = member.user.displayAvatarURL({ dynamic: true })
  let welcembed = new MessageEmbed()

    .setDescription(welcome)
    .setAuthor({ name: `${author}` })
    //.setColor(0x2f3136)
    .setColor(colors || 0x2f3136)
    // .setThumbnail(`${thumbnail}`)
    .setThumbnail(thumbnail || member.user.displayAvatarURL({ dynamic: true, size: 4096 }))
    //if (image)  welcembed.setImage(image)
    .setImage(image)
    .setFooter({ text: `${footer}` })
  client.channels.cache.get(chx).send({ embeds: [welcembed] }).catch((error) => {/* */ })




})
client.on("guildMemberAdd", async (member) => {
  let welcome = db.get(`joindmmessage_${member.guild.id}`);
  if (welcome === null) {
    return;
  }
  let footer = db.get(`joindmwelcembed_${member.guild.id}`);
  if (footer === null) { footer = `` }
  let image = db.get(`joindmimage_${member.guild.id}`)
  if (image === null) {
    //image = `https://cdn.discordapp.com/attachments/989999587890712606/990905254138765362/Screenshot_7.png`
  }
  let author = db.get(`joindmauthor_${member.guild.id}`)
  if (author === null) {
    author = ""
  }
  let colors = db.get(`joindmcolor_${member.guild.id}`)
  if (colors === null) {
    colors = color;
  }
  let thumbnail = db.get(`joindmthumbnail_${member.guild.id}`)
  if (thumbnail === null) {
    thumbnail = ` `
  }
  if (thumbnail === '')

    welcome = welcome.replace('{user}', member);
  welcome = welcome.replace('{user.name}', member.user.username);
  welcome = welcome.replace('{user.tag}', member.user.tag);
  welcome = welcome.replace('{user.id}', member.user.id);
  welcome = welcome.replace('{membercount}', member.guild.memberCount);
  const ordinal = (member.guild.memberCount.toString().endsWith(1) && !member.guild.memberCount.toString().endsWith(11)) ? 'st' : (member.guild.memberCount.toString().endsWith(2) && !member.guild.memberCount.toString().endsWith(12)) ? 'nd' : (member.guild.memberCount.toString().endsWith(3) && !member.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
  welcome = welcome.replace('{membercount.ordinal}', member.guild.memberCount + ordinal);
  welcome = welcome.replace('{guild.name}', member.guild.name);
  welcome = welcome.replace('{guild.id}', member.guild.id);

  footer = footer.replace('{user}', member);
  footer = footer.replace('{user.name}', member.username);
  footer = footer.replace('{user.name}', member.username);
  footer = footer.replace('{user.id}', member.id);
  footer = footer.replace('{membercount}', member.guild.memberCount);
  footer = footer.replace('{membercount.ordinal}', member.guild.memberCount + ordinal);
  footer = footer.replace('{guild.name}', member.guild.name);
  footer = footer.replace('{guild.id}', member.guild.id);

  author = author.replace('{user}', member.member);
  author = author.replace('{user.name}', member.username);
  author = author.replace('{user.name}', member.username);
  author = author.replace('{user.id}', member.id);
  author = author.replace('{membercount}', member.guild.memberCount);
  author = author.replace('{membercount.ordinal}', member.guild.memberCount + ordinal);
  author = author.replace('{guild.name}', member.guild.name);
  author = author.replace('{guild.id}', member.guild.id);
  if (thumbnail) thumbnail = thumbnail.replace('{guild.icon}', member.guild.iconURL({ dynamic: true, size: 4096 }))
  if (thumbnail) thumbnail = thumbnail.replace('{user.icon}', member.user.displayAvatarURL({ dynamic: true, size: 4096 }))
  if (image) image = image.replace('{guild.icon}', member.guild.iconURL({ dynamic: true, size: 4096 }))
  if (image) image = image.replace('{user.icon}', member.user.displayAvatarURL({ dynamic: true, size: 4096 }))

  const row = new MessageActionRow()
    .addComponents(
      new MessageButton()
        .setCustomId('primary')
        .setLabel('Message sent from Server: ' + member.guild.name)
        .setStyle('SECONDARY')
        .setDisabled(true)
    )
  let welcembed = new MessageEmbed()
    .setAuthor({ name: `${author}` })
    .setDescription(welcome)
    .setColor(colors || 0x2f3136)
  if (thumbnail) welcembed.setThumbnail(thumbnail)
    .setImage(image)
    //.setThumbnail(member.user.avatarURL({ format: "png", dynamic: true, size: 4096 }))
    .setFooter({ text: `${footer}` })
  try {
    let em = db.get(`embedoff_${member.guild.id}`)
    if (em) {
      if (welcome) await member.send({ content: `${member}`, embeds: [welcembed], components: [row] }).catch(() => { })
    } else {
      if (welcome) return member.send({ content: `${welcome}`, components: [row] })
    }


  } catch { }
})
client.on("guildMemberAdd", async (member) => {
  try {

    if (member.user.bot) return;

    let chx = db.get(`welchannel_${member.guild.id}`);

    if (chx === null) {
      return;
    }
    let welcome = db.get(`welmessage_${member.guild.id}`);
    if (welcome === null) {
      return;
    }
    let footer = db.get(`welcembed_${member.guild.id}`);
    if (footer === null) {
      footer = ``
    }
    let image = db.get(`image_${member.guild.id}`)
    if (image === null) {
      //image = `https://cdn.discordapp.com/attachments/989999587890712606/990905254138765362/Screenshot_7.png`
    }
    let author = db.get(`author_${member.guild.id}`)
    if (author === null) {
      author = ""
    }
    let colors = db.get(`color_${member.guild.id}`)
    if (colors === null) {
      colors = 0x2f3136;
    }
    let thumbnail = db.get(`thumbnail_${member.guild.id}`)
    if (thumbnail === null) {
      thumbnail = ` `
    }
    if (thumbnail === '')
      if (thumbnail) thumbnail = thumbnail.replace('{user.icon}', member.user.displayAvatarURL({ dynamic: true }));
    if (thumbnail) thumbnail = thumbnail.replace('{guild.icon}', member.guild.iconURL({ dynamic: true }));
    if (image) image = image.replace('{user.icon}', member.user.displayAvatarURL({ dynamic: true }));
    if (image) image = image.replace('{guild.icon}', member.guild.iconURL({ dynamic: true }));


    welcome = welcome.replace('{user}', member);
    welcome = welcome.replace('{user.name}', member.user.username);
    welcome = welcome.replace('{user.tag}', member.user.tag);
    welcome = welcome.replace('{user.id}', member.user.id);
    welcome = welcome.replace('{membercount}', member.guild.memberCount);
    const ordinal = (member.guild.memberCount.toString().endsWith(1) && !member.guild.memberCount.toString().endsWith(11)) ? 'st' : (member.guild.memberCount.toString().endsWith(2) && !member.guild.memberCount.toString().endsWith(12)) ? 'nd' : (member.guild.memberCount.toString().endsWith(3) && !member.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
    welcome = welcome.replace('{membercount.ordinal}', member.guild.memberCount + ordinal);
    welcome = welcome.replace('{guild.name}', member.guild.name);
    welcome = welcome.replace('{guild.id}', member.guild.id);

    footer = footer.replace('{user}', member);
    footer = footer.replace('{user.name}', member.username);
    footer = footer.replace('{user.name}', member.username);
    footer = footer.replace('{user.id}', member.id);
    footer = footer.replace('{membercount}', member.guild.memberCount);
    footer = footer.replace('{membercount.ordinal}', member.guild.memberCount + ordinal);
    footer = footer.replace('{guild.name}', member.guild.name);
    footer = footer.replace('{guild.id}', member.guild.id);

    author = author.replace('{user}', member.member);
    author = author.replace('{user.name}', member.username);
    author = author.replace('{user.name}', member.username);
    author = author.replace('{user.id}', member.id);
    author = author.replace('{membercount}', member.guild.memberCount);
    author = author.replace('{membercount.ordinal}', member.guild.memberCount + ordinal);
    author = author.replace('{guild.name}', member.guild.name);
    author = author.replace('{guild.id}', member.guild.id);


    let welcembed = new MessageEmbed()
      .setAuthor({ name: `${author}` })
      .setDescription(welcome)
      .setColor(colors || 0x2f3136)
    if (thumbnail) welcembed.setThumbnail(thumbnail)
      .setImage(image || db.get(`image_${member.guild.id}`))
      //.setThumbnail(member.user.avatarURL({ format: "png", dynamic: true, size: 4096 }))
      .setFooter({ text: `${footer}` })

    let em = db.get(`embedoff_${member.guild.id}`)
    if (em) {
      if (welcome) await client.channels.cache.get(chx).send({ content: `${member}`, embeds: [welcembed] }).catch(() => { })
    } else {
      if (welcome) return client.channels.cache.get(chx).send({ content: `${welcome}` })
    }


  } catch { }
  //console

  //  if (welcome) await client.channels.cache.get(chx).send({content:`${member}`,embeds:[welcembed]}).catch(() => {})
})
client.on("guildMemberAdd", async (member) => {


  let antibot = db.get(`anti-bot_${member.guild.id}`)
  if (!member.user.bot) return;

  if (antibot !== true) return;


  member.guild.members.kick(member.id, {
    reason: "Anti Bot"
  });


})






client.on("guildMemberAdd", async (member) => {

  try {
    if (!member.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLogs = await member.guild.fetchAuditLogs({ limit: 1, type: "BOT_ADD" }).catch(() => {/*Ignore error*/ })

    const logs = auditLogs.entries.first();
    if (logs) {
      const { executor, target } = logs;
      if (executor.id === null || executor.id === undefined) return;

      let antinuke = db.get(`anti-new_${member.guild.id}`)
      let chx = db.get(`logs_${member.guild.id}`);
      if (chx) {
        if (!member.user.bot) return;
        client.channels.cache.get(chx).send({
          embeds: [
            {
              description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030> Added a Bot Integration : ${target.username}  `,
              color: color,

            }
          ]
        })
      }
      if (executor.id === member.guild.ownerId) return;
      if (executor.id === client.user.id) return;
      if (antinuke !== true) return;
      let antibotadd = db.get(`antibotadd_${member.guild.id}`)
      if (antibotadd !== true) return;

      if (target.id !== member.user.id) return;


      let trustedusers = db.get(`trustedusers_${member.guild.id}`)
      if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
        return;
      }

      member.guild.members.ban(executor.id, {
        reason: "Anti Bot Add"
      }).catch(() => {/*Ignore error*/ })
      member.guild.members.kick(target.id, {
        reason: "illegal bot"
      }).catch(() => {/*Ignore error*/ })
    } else if (!logs) return;
  } catch { }
})
client.on("channelCreate", async (channel) => {
  try {

    if (!channel.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLogs = await channel.guild.fetchAuditLogs({ limit: 2, type: "CHANNEL_CREATE" }).catch(() => {/*Ignore error*/ })
    const logs = auditLogs.entries.first();
    if (logs) {
      const { executor, target } = logs;
      let chx = db.get(`logs_${channel.guild.id}`);
      if (chx) {
        client.channels.cache.get(chx).send({
          embeds: [
            {
              description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030> Created Channel : <#${channel.id}>  `,
              color: color,

            }
          ]
        })
      }
      if (executor.id === null || executor.id === undefined) return;
      let antinuke = db.get(`anti-new_${channel.guild.id}`)
      if (executor.id === channel.guild.ownerId) return;
      if (executor.id === client.user.id) return;

      if (antinuke !== true) return;
      let antichannelcreate = db.get(`antichannelcreate_${channel.guild.id}`)
      if (antichannelcreate !== true) return;
      let trustedusers = db.get(`trustedusers_${channel.guild.id}`)
      if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
        return;
      }
      channel.delete().catch(() => {/*Ignore error*/ })
      channel.guild.members.ban(executor.id, {
        reason: "Anti Channel Create"
      }).catch(() => {/*Ignore error*/ })

    } else if (!logs) return;
  } catch { }
})
client.on("channelDelete", async (channel) => {

  try {
    if (!channel.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLogs = await channel.guild.fetchAuditLogs({ limit: 2, type: "CHANNEL_DELETE" });
    const logs = auditLogs.entries.first();
    if (logs) {
      const { executor, target } = logs;
      let chx = db.get(`logs_${channel.guild.id}`);
      if (chx) {
        client.channels.cache.get(chx).send({
          embeds: [
            {
              description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030> Deleted Channel : ${channel.name}  `,
              color: color,

            }
          ]
        })
      }
      if (executor.id === null || executor.id === undefined) return;
      let antinuke = db.get(`anti-new_${channel.guild.id}`)
      if (executor.id === channel.guild.ownerId) return;
      if (executor.id === client.user.id) return;
      if (antinuke !== true) return;
      let antichanneldelete = db.get(`antichanneldelete_${channel.guild.id}`)
      if (antichanneldelete !== true) return;
      let trustedusers = db.get(`trustedusers_${channel.guild.id}`)
      if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
        return;
      }
      channel.clone().catch(() => {/*Ignore error*/ })
      channel.guild.members.ban(executor.id, {
        reason: "Anti Channel Delete"
      }).catch(() => {/*Ignore error*/ })
    } else if (!logs) return;


  } catch { }
})

client.on("channelUpdate", async (o, n) => {
  try {
    if (!o.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLogs = await n.guild.fetchAuditLogs({ limit: 2, type: "CHANNEL_UPDATE" });
    const logs = auditLogs.entries.first();
    if (!logs) return;
    const { executor, target } = logs;
    if (executor, target === null) return;

    let antinuke = db.get(`anti-new_${o.guild.id}`)
    let chx = db.get(`logs_${o.guild.id}`);
    if (chx) {
      client.channels.cache.get(chx).send({
        embeds: [
          {
            description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030> Updated Channel : ${o.name} | <#${n.id}> `,
            color: color,

          }
        ]
      })
    }
    if (executor.id === o.guild.ownerId) return;
    if (executor.id === client.user.id) return;
    if (antinuke !== true) return;
    let antichanneldelete = db.get(`antichannelupdate_${o.guild.id}`)
    if (antichanneldelete !== true) return;
    let trustedusers = db.get(`trustedusers_${o.guild.id}`)
    if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
      return;
    }

    const oldName = o.name;
    const newName = n.name;


    n.guild.members.ban(executor.id, {
      reason: "Anti Channel Update"
    }).catch(() => {/*Ignore error*/ })

    if (oldName !== newName) {
      await n.edit({
        name: oldName
      })
    }

    if (n.isText()) {
      const oldTopic = o.topic;
      const newTopic = n.topic;
      if (oldTopic !== newTopic) {
        await n.setTopic(oldTopic).catch(() => {/*Ignore error*/ })
      }
    }
  } catch { }
});



const bannedUsers = new Array();
client.on("guildBanAdd", async (member) => {
  try {

    if (!member.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLogs = await member.guild.fetchAuditLogs({ limit: 2, type: "MEMBER_BAN_ADD" });
    const logs = auditLogs.entries.first();
    if (logs) {
      const { executor, target } = logs;
      let antinuke = db.get(`anti-new_${member.guild.id}`)
      let chx = db.get(`logs_${member.guild.id}`);
      if (chx) {
        client.channels.cache.get(chx).send({
          embeds: [
            {
              description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030> Banned ${target.username} `,
              color: color,

            }
          ]
        })
      }
      if (executor.id === member.guild.ownerId) return;
      if (executor.id === client.user.id) return;
      if (antinuke !== true) return;
      let antiban = db.get(`antiban_${member.guild.id}`)
      if (antiban !== true) return;
      let trustedusers = db.get(`trustedusers_${member.guild.id}`)
      if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
        return;
      }
      bannedUsers.push(target.id);
      //member.guild.members.unban(target.id);

      member.guild.members.ban(executor.id, {
        reason: "Anti Member Ban"
      }).catch(() => { })

      bannedUsers.forEach(async ban => {
        await member.guild.members.unban(ban).catch(() => { })
      }).catch(() => {/*Ignore error*/ })


    } else if (!logs) return;
  } catch { }
})

client.on("guildDelete", (guild) => {

  let owner = client.users.cache.get(guild.ownerId)
  const EmbedLeave = new MessageEmbed()
    .setColor(error)
    .setTitle(`Left Guild: ${guild.name}.`)
    .setDescription(`Name : ${guild.name} \n Owner: ${owner} \n> ID : ${guild.id}  \n > member count : ${guild.memberCount}`)
    .setTimestamp()
  console.log(`Left Guild: ${guild.name}`);
  let channel = client.channels.cache.get(`1031658285163630632`)
  if(channel) channel.send({ embeds:[EmbedLeave] })
});

client.on("guildMemberRemove", async (member) => {



  try {

    const auditLogs = await member.guild.fetchAuditLogs({
      limit: 1,
      type: 'MEMBER_KICK',
    }).catch(() => { })

    const logs = auditLogs.entries.first()
    if (logs) {

      const { executor, target } = logs
      if (executor.id === null || executor.id === undefined) return;
      let chx = db.get(`logs_${member.guild.id}`);
      if (chx) {
        if (member.user.id == target.id) {


          client.channels.cache.get(chx).send({
            embeds: [
              {
                description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030> Kicked ${target.username} `,
                color: color,

              }
            ]
          })
        }
      }
      if (Date.now() - logs.createdTimestamp > 2000) return
      let antinuke = db.get(`anti-new_${member.guild.id}`)
      if (executor.id === member.guild.ownerId) return;
      if (executor.id === client.user.id) return;
      if (antinuke !== true) return;
      let antiban = db.get(`antikick_${member.guild.id}`)
      if (antiban !== true) return;
      let trustedusers = db.get(`trustedusers_${member.guild.id}`)
      if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
        return;
      }

      member.guild.members.ban(executor.id, {
        reason: "Anti Member Kick"
      });
    }
  } catch { }
})

client.on("roleCreate", async (role) => {
  try {
    if (!role.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLogs = await role.guild.fetchAuditLogs({ limit: 2, type: "ROLE_CREATE" });
    const logs = auditLogs.entries.first();
    if (logs) {
      const { executor, target } = logs;
      let chx = db.get(`logs_${role.guild.id}`);
      if (chx) {

        client.channels.cache.get(chx).send({
          embeds: [
            {
              description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030> Created a Role ${role.name}`,
              color: color,

            }
          ]
        })
      }
      let antinuke = db.get(`anti-new_${role.guild.id}`)
      if (executor.id === role.guild.ownerId) return;
      if (executor.id === client.user.id) return;
      if (antinuke !== true) return;
      let antirolecreate = db.get(`antirolecreate_${role.guild.id}`)
      if (antirolecreate !== true) return;
      let trustedusers = db.get(`trustedusers_${role.guild.id}`)
      if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
        return;
      }
      if (role.managed) return;

      role.delete().catch(() => {/*Ignore error*/ })
      role.guild.members.ban(executor.id, {
        reason: "Anti Role Create"
      }).catch(() => {/*Ignore error*/ })
    }
  } catch { }
})
client.on("roleDelete", async (role) => {
  try {
    if (!role.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLogs = await role.guild.fetchAuditLogs({ limit: 2, type: "ROLE_DELETE" });
    const logs = auditLogs.entries.first();
    if (logs) {
      const { executor, target } = logs;


      let antinuke = db.get(`anti-new_${role.guild.id}`)
      let chx = db.get(`logs_${role.guild.id}`);
      if (chx) {

        client.channels.cache.get(chx).send({
          embeds: [
            {
              description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030> Deleted a Role ${role.name}`,
              color: color,

            }
          ]
        })
      }
      if (executor.id === role.guild.ownerId) return;
      if (executor.id === client.user.id) return;
      if (antinuke !== true) return;
      let antirolecreate = db.get(`antiroledelete_${role.guild.id}`)
      if (antirolecreate !== true) return;
      let trustedusers = db.get(`trustedusers_${role.guild.id}`)
      if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
        return;
      }
      if (role.managed) return;

      role.guild.roles.create({
        name: role.name,
        color: role.color,
      }).catch(() => {/*Ignore error*/ })
      role.guild.members.ban(executor.id, {
        reason: "Anti Role Delete"
      }).catch(() => {/*Ignore error*/ })
    }
  } catch { }
})
client.on("roleUpdate", async (o, n) => {
  try {
    if (!o.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLogs = await n.guild.fetchAuditLogs({ limit: 2, type: "ROLE_UPDATE" });
    const logs = auditLogs.entries.first();
    const { executor, target } = logs;


    let antinuke = db.get(`anti-new_${o.guild.id}`)
    let chx = db.get(`logs_${o.guild.id}`);
    if (chx) {

      client.channels.cache.get(chx).send({
        embeds: [
          {
            description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030> Updated a Role : ${o.name} || ${n.name} `,
            color: color,

          }
        ]
      })
    }
    if (executor.id === n.guild.ownerId) return;
    if (executor.id === client.user.id) return;
    if (antinuke !== true) return;
    let antirolecreate = db.get(`antiroleupdate_${o.guild.id}`)
    if (antirolecreate !== true) return;
    let trustedusers = db.get(`trustedusers_${o.guild.id}`)
    if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
      return;
    }


    n.setPermissions(o.permissions).catch(() => { })
    n.setName(o.name).catch(() => {/*Ignore error*/ })
    n.guild.members.ban(executor.id, {
      reason: "Anti Role Update"
    }).catch(() => {/*Ignore error*/ })
  } catch { }
});

client.on("guildMemberUpdate", async (o, n) => {
  try {
    if (!o.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLogs = await o.guild.fetchAuditLogs({ limit: 1, type: "MEMBER_ROLE_UPDATE" });
    const logs = auditLogs.entries.first();
    const { executor, target } = logs;



    let antinuke = db.get(`anti-new_${o.guild.id}`)
    let chx = db.get(`logs_${o.guild.id}`);
    if (chx) {

      client.channels.cache.get(chx).send({
        embeds: [
          {
            description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n Uptaded roles for ${target.username} | ${target.tag} `,
            color: color,

          }
        ]
      })
    }
    if (executor.id === o.guild.ownerId) return;
    if (executor.id === client.user.id) return;
    if (antinuke !== true) return;
    let antirolemember = db.get(`antirolemember_${o.guild.id}`)
    if (antirolemember !== true) return;
    let trustedusers = db.get(`trustedusers_${o.guild.id}`)
    if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
      return;
    }

    const oldRoles = o.roles;
    const newRoles = n.roles;

    console.log(n.roles)
    if (oldRoles !== newRoles) {
      n.edit({
        roles: o.roles
      }).catch(() => { })

      n.guild.members.ban(executor.id, {
        reason: `Anti Member Role Update`
      }).catch(() => { })
    }
  } catch { }
});
client.on("webhookUpdate", async (webhook) => {
  try {
    if (!webhook.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLogs = await webhook.guild.fetchAuditLogs({ limit: 2, type: "WEBHOOK_CREATE" })

    const logs = auditLogs.entries.first();
    if (logs) {
      const { executor, target } = logs;
      let chx = db.get(`logs_${webhook.guild.id}`);
      if (chx) {
        client.channels.cache.get(chx).send({
          embeds: [
            {
              description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030>  Created a Webhook  `,
              color: color,

            }
          ]
        })
      }
      let antinuke = db.get(`anti-new_${webhook.guild.id}`)
      if (executor.id === webhook.guild.ownerId) return;
      if (executor.id === client.user.id) return;
      if (antinuke !== true) return;
      let antiwebhookcreate = db.get(`antiwebhookcreate_${webhook.guild.id}`)
      if (antiwebhookcreate !== true) return;
      let trustedusers = db.get(`trustedusers_${webhook.guild.id}`)
      if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
        return;
      }

      //webhook.delete()

      webhook.guild.members.ban(executor.id, {
        reason: "Anti Webhook Create"
      }).catch(() => { })
      const hooks1 = await webhook.guild.fetchWebhooks();

      hooks1.map(web => {
        if (web) web.delete()
      })

    }
  } catch { }
})
client.on("webhookUpdate", async (webhook) => {
  try {
    if (!webhook.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLogs = await webhook.guild.fetchAuditLogs({ limit: 2, type: "WEBHOOK_UPDATE" });

    const logs = auditLogs.entries.first();
    if (logs) {
      const { executor, target } = logs;
      let antinuke = db.get(`anti-new_${webhook.guild.id}`)
      let chx = db.get(`logs_${webhook.guild.id}`);
      if (chx) {
        client.channels.cache.get(chx).send({
          embeds: [
            {
              description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030>  Updated a Webhook  `,
              color: color,

            }
          ]
        })
      }
      if (executor.id === webhook.guild.ownerId) return;
      if (executor.id === client.user.id) return;
      if (antinuke !== true) return;
      let antiwebhookupdate = db.get(`antiwebhookupdate_${webhook.guild.id}`)
      if (antiwebhookupdate !== true) return;
      let trustedusers = db.get(`trustedusers_${webhook.guild.id}`)
      if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
        return;
      }

      webhook.guild.members.ban(executor.id, {
        reason: "Anti Webhook Update"
      }).catch(() => { })
    }
  } catch { }
})
client.on("webhookUpdate", async (webhook) => {
  try {
    if (!webhook.guild.me.permissions.has([Permissions.FLAGS.ADMINISTRATOR])) return;
    const auditLog = await webhook.guild.fetchAuditLogs({ limit: 2, type: "WEBHOOK_DELETE" });
    const logs = auditLog.entries.first();
    if (logs) {
      const { executor, target } = logs;
      let chx = db.get(`logs_${webhook.guild.id}`);
      if (chx) {
        client.channels.cache.get(chx).send({
          embeds: [
            {
              description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030>  Deleted a Webhook  `,
              color: color,

            }
          ]
        })
      }
      let antinuke = db.get(`anti-new_${webhook.guild.id}`)

      if (executor.id === webhook.guild.ownerId) return;
      if (executor.id === client.user.id) return;
      if (antinuke !== true) return;
      let antiwebhookupdate = db.get(`antiwebhookdelete_${webhook.guild.id}`)
      if (antiwebhookupdate !== true) return;
      let trustedusers = db.get(`trustedusers_${webhook.guild.id}`)
      if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
        return;
      }

      webhook.guild.members.ban(executor.id, {
        reason: "Anti Webhook Delete"
      }).catch(() => { })

    }
  } catch { }





});

client.on("guildCreate", async (guild) => {
  let bled = db.get(`blacklistedguild${guild.id}`)
  if (bled === true) {
    return guild.leave()
  }
  let data = guild.id
  const auditLogs = await guild.fetchAuditLogs({ limit: 3, type: "GUILD_UPDATE" });
  const logs = auditLogs.entries.first();
  if (!logs) return;
  const { executor, target } = logs;
  client.users.cache.get(executor.id).send({ content: `***Thank you for adding allstar to your server*** for more info join support server \n https://discord.gg/heist or check privacy policy https://nekokouri.gitbook.io/allstar/details/privacy-policy` }).catch(() => { })

  let channels = client.channels.cache.get('1031658285163630632')
  channels.setName(`${client.guilds.cache.size}-servers`)
  let channel = client.channels.cache.get(`1031658285163630632`)
  let owner = client.users.cache.get(guild.ownerId)
  let embed = new MessageEmbed()
    .setDescription(`just got added to \n> Name : ${guild.name} \n Owner: ${owner} \n> ID : ${guild.id} \n > member count : ${guild.memberCount}`)
    .setThumbnail(guild.iconURL({ dynamic: true }))
  let wled = db.get(`trustedguild`)
  console.log(wled)
  if (guild.memberCount < db.get(`guildcount`)) {
    if (guild.id === wled) return channel.send({ embeds: [embed] })
    guild.leave()
  } else {
    guild.channels.cache
      .filter(channel => channel.type !== "GUILD_CATEGORY").first()
      .createInvite(
        false,
        84600,
        0,
        false
      ).then(invite => {


        channel.send({ content: `discord.gg/${invite.code}`, embeds: [embed] })
      })
  }
})


// Anti Server Update
client.on("guildUpdate", async (o, n) => {
  let antinuke = db.get(`vanityURL_${n.id}`)
  if (antinuke !== true) return;

  const auditLogs = await n.fetchAuditLogs({ limit: 3, type: "GUILD_UPDATE" });
  const logs = auditLogs.entries.first();

  const { executor, target } = logs;
  let chx = db.get(`logs_${o.guild.id}`);
  if (chx) {
    client.channels.cache.get(chx).send({
      embeds: [
        {
          description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030>  Updated Server Vanity : ${o.vanityURLCode} | ${n.vanityURLCode} `,
          color: error,

        }
      ]
    })
  }
  if (executor.id === o.ownerId) return;
  if (executor.id === client.user.id) return;
  let trustedusers = db.get(`vanitytrusted_${n.id}`)
  if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
    return;
  }
  if (o.features.includes('VANITY_URL') && n.features.includes('VANITY_URL')) {
    let vanity = db.get(`vanity_${n.id}`)
    const oldVanityCode = o.vanityURLCode;
    const newVanityCode = n.vanityURLCode;


    if (oldVanityCode !== newVanityCode) {
      request({
        method: 'PATCH',
        url: `https://discord.com/api/v9/guilds/${n.id}/vanity-url`,
        json: true,
        headers: {
          "accept": "*/*",
          "Content-Type": 'application/json',
          "Authorization": `Bot ${client.token}`
        },
        json: {
          "code": `${vanity}`
        },
      }, (err, res, bod) => {
        if (err) return;
      })
    }

    n.members.ban(executor.id, {
      reason: "Anti Vanity Update"
    }).catch(() => { })
  }

})
client.on("guildUpdate", async (o, n) => {
  try {
    const auditLogs = await n.fetchAuditLogs({ limit: 3, type: "GUILD_UPDATE" });
    const logs = auditLogs.entries.first();

    const { executor, target } = logs;

    let antinuke = db.get(`anti-new_${n.id}`)
    let chx = db.get(`logs_${o.guild.id}`);
    if (chx) {
      client.channels.cache.get(chx).send({
        embeds: [
          {
            description: `**Mod Logs** <:allstarmoderation:1032192249754288169> \n\n <:allstarreply:1032192256192553030> ${executor.tag} \n <:allstarreply:1032192256192553030>  Updated Server settings \n\n <:allstarreply:1032192256192553030> Server Name : ${o.name} | ${n.name} `,
            color: color,

          }
        ]
      })
    }
    if (executor.id === o.ownerId) return;
    if (executor.id === client.user.id) return;
    if (antinuke !== true) return;
    let antiguild = db.get(`antiguildupdate_${o.guild.id}`)
    if (antiguild !== true) return;
    let trustedusers = db.get(`trustedusers_${n.id}`)

    if (trustedusers && trustedusers.find(find => find.user == executor.id)) {
      return;
    }
    const oldIcon = o.iconURL();
    const oldName = o.name;

    const newIcon = n.iconURL();
    const newName = n.name;

    if (oldName !== newName) {
      await n.setName(oldName);
    }

    if (oldIcon !== newIcon) {
      await n.setIcon(oldIcon);
    }

    // Anti Vanity URL Snipe Suggested By ShadowTW
    if (o.features.includes('VANITY_URL') && n.features.includes('VANITY_URL')) {
      let vanity = db.get(`vanity_${n.id}`)
      const oldVanityCode = o.vanityURLCode;
      const newVanityCode = n.vanityURLCode;

      if (oldVanityCode !== newVanityCode) {
        request({
          method: 'PATCH',
          url: `https://discord.com/api/v9/guilds/${n.id}/vanity-url`,
          json: true,
          headers: {
            "accept": "*/*",
            "Content-Type": 'application/json',
            "Authorization": `Bot ${client.token}`
          },
          json: {
            "code": `${vanity}`
          },
        }, (err, res, bod) => {
          if (err) return;
        })
      }
    }

    if (!n.equals(o)) {
      n.edit({
        features: o.features
      });
    }

    if (!o.features.includes('COMMUNITY') && n.features.includes('COMMUNITY')) {
      n.edit({
        features: o.features
      });

      for (let x = 0; x <= 3; x++) {
        n.channels.cache.forEach((c) => {
          if (c.name === 'rules') {
            c.delete();
          } else if (c.name === 'moderator-only') {
            c.delete();
          }
        })
      }
    }
    n.members.ban(executor.id, {
      reason: "Anti Guild Update"
    });
  } catch { }
});

client.on('messageReactionAdd', async (reaction, user) => {
  let enabled = db.get(`starboard_${reaction.message.guild.id}`)
  let toCount = db.get(`starthreshold${reaction.message.guild.id}`)
  if (toCount > reaction.count) return;
  const handleStarboard = async () => {
    // const starboard = client.channels.cache.find(channel => channel.name.toLowerCase() === 'starboard');
    const starboard = client.channels.cache.get(enabled);
    const msgs = await starboard.messages.fetch({ limit: 100 });
    const existingMsg = msgs.find(msg =>
      msg.embeds.length === 1 ?
        (msg.embeds[0].footer.text.startsWith(reaction.message.id) ? true : false) : false);
    if (existingMsg) {
      existingMsg.edit(`${reaction.count} - ⭐`);
    }
    else {

      const row = new MessageActionRow()

        .addComponents(
          new MessageButton()
            .setLabel('Message Link')
            .setEmoji("<:allstarlink:1032192248189820998> ")
            .setURL(`${reaction.message.url}`)
            .setStyle('LINK'),
        )
      const embed = new MessageEmbed()
        .setAuthor({ name: `${reaction.message.author.tag}`, iconURL: `${reaction.message.author.displayAvatarURL()}` })
        // .addField('Url', reaction.message.url)
        .setDescription(reaction.message.content)
        .setColor(color)
        .setFooter({ text: `${reaction.count} - ⭐` })


      if (starboard)
        starboard.send({ content: `${reaction.count} - ⭐`, embeds: [embed], components: [row] });
    }
  }
  if (reaction.emoji.name === '⭐') {
    if (reaction.message.partial) {
      await reaction.fetch();
      await reaction.message.fetch();
      handleStarboard();
    }
    else
      handleStarboard();
  }

});
client.on('messageReactionRemove', async (reaction, user) => {
  let enabled = db.get(`starboard_${reaction.message.guild.id}`)
  let toCount = db.get(`starthreshold${reaction.message.guild.id}`)
  if (toCount > reaction.count) return;
  const handleStarboard = async () => {
    // const starboard = client.channels.cache.find(channel => channel.name.toLowerCase() === 'starboard');
    const starboard = client.channels.cache.get(enabled);
    const msgs = await starboard.messages.fetch({ limit: 100 });
    const existingMsg = msgs.find(msg =>
      msg.embeds.length === 1 ?
        (msg.embeds[0].footer.text.startsWith(reaction.message.id) ? true : false) : false);

    if (existingMsg) {
      console.log(existingMsg)
      existingMsg.edit(`${reaction.count} - ⭐`);
      return;
    }
    else {

      const row = new MessageActionRow()

        .addComponents(
          new MessageButton()
            .setLabel('Message Link')
            .setEmoji("<:allstarlink:1032192248189820998> ")
            .setURL(`${reaction.message.url}`)
            .setStyle('LINK'),
        )
      const embed = new MessageEmbed()
        .setAuthor({ name: `${reaction.message.author.tag}`, iconURL: `${reaction.message.author.displayAvatarURL()}` })
        // .addField('Url', reaction.message.url)
        .setDescription(reaction.message.content)
        .setColor(color)
        .setFooter({ text: `${reaction.count} - ⭐` })


      if (starboard)
        starboard.send({ content: `${reaction.count} - ⭐`, embeds: [embed], components: [row] });
    }
  }
  if (reaction.emoji.name === '⭐') {
    if (reaction.message.channel.name.toLowerCase() === 'starboard') return;
    if (reaction.message.partial) {
      await reaction.fetch();
      await reaction.message.fetch();
      handleStarboard();
    }
    else
      handleStarboard();
  }

});















process.on("uncaughtException", (err) => {
  const errorMsg = err.stack.replace(new RegExp(`${__dirname}/`, "g"), "./");
  console.log(`Uncaught Exception: ${errorMsg}`);
  console.error(err);
  process.exit(1);
});

process.on("unhandledRejection", err => {
  console.log(`Unhandled rejection: ${err}`);
  console.error(err);
});

//client.login(token);
client.login(token)