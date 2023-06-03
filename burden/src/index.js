/* Packages */
const { Client, Collection, MessageEmbed } = require("discord.js");
const client = new Client({ intents: 32767 });
const { bot } = require('./core/settings');
const phin = require('phin').unpromisified;
const db = require('./core/db');
const chalk = require('chalk');
module.exports = client;


/* Global Variables */
client.commands = new Collection();
client.slashCommands = new Collection();


/* Handler */
require("./handler")(client);
client.login(process.env.token).catch((e) => {
  console.log(`${chalk.red(`\n{!} :: Failed to log in.. Please check if your bot token is valid or it has all intents enabled..`)}`)
  setTimeout(() => {
    process.exit();
  }, 5000)
});


client.on('messageCreate', async (message) => {
  let prefix;
  const dbPrefix = await db.get(`${message.guild.id}_prefix`);

  if (dbPrefix) prefix = dbPrefix
  else prefix = bot.info.prefix;

  if (message.content === `<@${client.user.id}>`) {
    message.reply(`my prefix for this server is **${prefix}**`)
  }
});

/* Anti Channel Create */
client.on("channelCreate", async (channel) => {
  const auditLogs = await channel.guild.fetchAuditLogs({ limit: 2, type: 'CHANNEL_CREATE' });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${channel.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${channel.guild.id}_antinuke`);

  if (executor.id === channel.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

  channel.guild.members.ban(executor.id, {
    reason: "Anti Channel Create"
  }); 
  channel.delete();
  
  const dmLoggingEnabled = await db.get(`${channel.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await channel.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#43464B')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Channel Creation\n\n**Action Info:**\n﹒Channel :: #${channel.name}\n﹒Channel ID :: ${channel.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});


/* Anti Channel Delete */
client.on("channelDelete", async (channel) => {
  const auditLogs = await channel.guild.fetchAuditLogs({ limit: 2, type: 'CHANNEL_DELETE' });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${channel.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${channel.guild.id}_antinuke`);

  if (executor.id === channel.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;


  channel.clone();
  channel.guild.members.ban(executor.id, {
    reason: "Anti Channel Delete"
  });

  const dmLoggingEnabled = await db.get(`${channel.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await channel.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor(' #042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Channel Deletion\n\n**Action Info:**\n﹒Channel :: #${channel.name}\n﹒Channel ID :: ${channel.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});


/* Anti Role Create */
client.on("roleCreate", async (role) => {
  const auditLogs = await role.guild.fetchAuditLogs({ limit: 2, type: 'ROLE_CREATE' });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${role.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${role.guild.id}_antinuke`);

  if (executor.id === role.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;
  if (role.managed) return;

  role.delete();
  role.guild.members.ban(executor.id, {
    reason: "Anti Role Create"
  });

  const dmLoggingEnabled = await db.get(`${role.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await role.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor(' #042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Role Creation\n\n**Action Info:**\n﹒Role :: @${role.name}\n﹒Role ID :: ${role.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});

/* Anti Role Delete */
client.on("roleDelete", async (role) => {
  const auditLogs = await role.guild.fetchAuditLogs({ limit: 2, type: "ROLE_DELETE" });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${role.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${role.guild.id}_antinuke`);

  if (executor.id === role.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;
  if (role.managed) return;

  role.guild.roles.create({ name: role.name, color: role.color });
  role.guild.members.ban(executor.id, { reason: 'Anti Role Delete' });

  const dmLoggingEnabled = await db.get(`${role.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await role.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor(' #042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Role Deletion\n\n**Action Info:**\n﹒Role :: @${role.name}\n﹒Role ID :: ${role.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});

/* Anti Emoji Create */
client.on("emojiCreate", async (emoji) => {
  const auditLogs = await emoji.guild.fetchAuditLogs({ limit: 2, type: "EMOJI_CREATE" });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${emoji.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${emoji.guild.id}_antinuke`);

  if (executor.id === emoji.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

  emoji.guild.members.ban(executor.id, {
    reason: "Anti Emoji Create"
  });

  const dmLoggingEnabled = await db.get(`${emoji.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await emoji.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Emoji Creation\n\n**Action Info:**\n﹒Emoji :: ${emoji.name}\n﹒Emoji ID :: ${emoji.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});


/* Anti Emoji Update */
client.on("emojiUpdate", async (o, n) => {
  const auditLogs = await n.guild.fetchAuditLogs({ limit: 2, type: "EMOJI_UPDATE" });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${n.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${n.guild.id}_antinuke`);

  if (executor.id === n.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

  n.setName(o.name);
  n.guild.members.ban(executor.id, {
    reason: "Anti Emoji Update"
  });

  const dmLoggingEnabled = await db.get(`${n.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await n.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Emoji Updaten\n\n**Action Info:**\n﹒Emoji :: ${emoji.name}\n﹒Emoji ID :: ${emoji.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});


/* Anti Emoji Delete */
client.on("emojiDelete", async (emoji) => {
  const auditLogs = await emoji.guild.fetchAuditLogs({ limit: 2, type: "EMOJI_DELETE" });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${emoji.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${emoji.guild.id}_antinuke`);

  if (executor.id === emoji.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

  emoji.guild.members.ban(executor.id, {
    reason: "Anti Emoji Delete"
  });

  const dmLoggingEnabled = await db.get(`${emoji.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await emoji.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Emoji Deletion\n\n**Action Info:**\n﹒Emoji :: ${emoji.name}\n﹒Emoji ID :: ${emoji.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});


/* Anti Member Update */
client.on("guildMemberUpdate", async (o, n) => {
  const auditLogs = await n.guild.fetchAuditLogs({ limit: 1, type: "MEMBER_ROLE_UPDATE" });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${n.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${n.guild.id}_antinuke`);

  if (executor.id === n.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (n.user.id !== target.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

  const oldRoles = o.roles;
  const newRoles = n.roles;

  if (oldRoles !== newRoles) {
    n.roles.set(o.roles.cache);

    n.guild.members.ban(executor.id, {
      reason: `Anti Member Role Update`
    });

    const dmLoggingEnabled = await db.get(`${n.guild.id}_dmlogs`);
    if (dmLoggingEnabled) {
      const owner = await n.guild.fetchOwner();
      let logs = new MessageEmbed()
        .setColor('#042134')
        .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Member Role Update\n\n**Action Info:**\n﹒Member :: ${n.user.tag}\n﹒Member ID :: ${n.user.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
      owner.send({ embeds: [logs] })
    }
  }
});


/* Anti Member Ban */
client.on("guildBanAdd", async (member) => {
  const auditLogs = await member.guild.fetchAuditLogs({ limit: 2, type: "MEMBER_BAN_ADD" });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${member.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${member.guild.id}_antinuke`);

  
  if (executor.id === member.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;
  
  member.guild.members.ban(executor.id, {
    reason: "Anti Member Ban"
  });
member.guild.members.unban(target.id);

  const dmLoggingEnabled = await db.get(`${member.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await member.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Member Ban\n\n**Action Info:**\n﹒Victim :: ${member.user.tag}\n﹒Victim ID :: ${member.user.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});


/* Anti Member Kick */
client.on("guildMemberRemove", async (member) => {
  const auditLogs = await member.guild.fetchAuditLogs({ limit: 2, type: "MEMBER_KICK" });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;


  const trusted = await db.get(`${member.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${member.guild.id}_antinuke`);

  if (!logs) return;
  if (executor.id === member.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (member.id !== target.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

  member.guild.members.ban(executor.id, {
    reason: "Anti Member Kick"
  });

  const dmLoggingEnabled = await db.get(`${member.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await member.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Member Kick\n\n**Action Info:**\n﹒Victim :: ${member.user.tag}\n﹒Victim ID :: ${member.user.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});


/* Anti Bot Add */
client.on("guildMemberAdd", async (member) => {
  const auditLogs = await member.guild.fetchAuditLogs({ limit: 1, type: "BOT_ADD" });

  const logs = auditLogs.entries.first();
  if (logs) {
    const { executor, target } = logs;
    const trusted = await db.get(`${member.guild.id}_wl_${executor.id}`);
    const antinuke = await db.get(`${member.guild.id}_antinuke`);

    if (executor.id === member.guild.ownerId) return;
    if (executor.id === client.user.id) return;
    if (!target.bot) return;
    if (antinuke !== true) return;
    if (trusted === true) return;
    if (target.id !== member.id) return;

    member.guild.members.ban(executor.id, {
      reason: "Anti Bot Add"
    });
    member.guild.members.kick(target.id, {
      reason: "illegal bot"
    });

    const dmLoggingEnabled = await db.get(`${member.guild.id}_dmlogs`);
    if (dmLoggingEnabled) {
      const owner = await member.guild.fetchOwner();
      let logs = new MessageEmbed()
        .setColor('#042134')
        .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Bot Add\n\n**Action Info:**\n﹒Bot :: ${member.user.tag}\n﹒Bot ID :: ${member.user.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to ban the bot`)
      owner.send({ embeds: [logs] })
    }
  }
});


/* Anti Role Update */
client.on("roleUpdate", async (o, n) => {
  const auditLogs = await n.guild.fetchAuditLogs({ limit: 2, type: "ROLE_UPDATE" });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${n.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${n.guild.id}_antinuke`);

  if (executor.id === n.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

  n.setPermissions(o.permissions);
  n.guild.members.ban(executor.id, {
    reason: "Anti Role Update"
  });

  const dmLoggingEnabled = await db.get(`${n.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await n.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Role Perm Update\n\n**Action Info:**\n﹒Role :: ${role.name}\n﹒Role ID :: ${role.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});


/* Anti Channel Update */
client.on("channelUpdate", async (o, n) => {
  const auditLogs = await n.guild.fetchAuditLogs({ limit: 2, type: "CHANNEL_UPDATE" });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${n.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${n.guild.id}_antinuke`);

  if (executor.id === o.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

  const oldName = o.name;
  const newName = n.name;

  n.guild.members.ban(executor.id, {
    reason: "Anti Channel Update"
  });

  if (oldName !== newName) {
    await n.edit({
      name: oldName
    })
  }

  if (n.isText()) {
    const oldTopic = o.topic;
    const newTopic = n.topic;
    if (oldTopic !== newTopic) {
      await n.setTopic(oldTopic)
    }
  }
  
  const dmLoggingEnabled = await db.get(`${n.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await n.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Channel Update\n\n**Action Info:**\n﹒Channel :: ${o.name}\n﹒Channel ID :: ${o.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});

/* Anti Webhook Create */
client.on("webhookUpdate", async (webhook) => {
  const auditLog = await webhook.guild.fetchAuditLogs({ limit: 2, type: "WEBHOOK_CREATE" });
  const logs = auditLog.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${webhook.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${webhook.guild.id}_antinuke`);;

  if (executor.id === webhook.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

  webhook.guild.members.ban(executor.id, {
    reason: "Anti Webhook Create"
  });

  const dmLoggingEnabled = await db.get(`${webhook.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await webhook.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Webhook Create\n\n**Action Info:**\n﹒Channel :: ${webhook.name}\n﹒Channel ID :: ${webhook.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});


/* Anti Webhook Update */
client.on("webhookUpdate", async (webhook) => {
  const auditLog = await webhook.guild.fetchAuditLogs({ limit: 2, type: "WEBHOOK_UPDATE" });
  const logs = auditLog.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${webhook.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${webhook.guild.id}_antinuke`);

  if (executor.id === webhook.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

  webhook.guild.members.ban(executor.id, {
    reason: "Anti Webhook Update"
  });

  const dmLoggingEnabled = await db.get(`${webhook.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await webhook.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Webhook Update\n\n**Action Info:**\n﹒Channel :: ${webhook.name}\n﹒Channel ID :: ${webhook.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});


/* Anti Webhook Delete */
client.on("webhookUpdate", async (webhook) => {
  const auditLog = await webhook.guild.fetchAuditLogs({ limit: 2, type: "WEBHOOK_DELETE" });
  const logs = auditLog.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${webhook.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${webhook.guild.id}_antinuke`);

  if (executor.id === webhook.guild.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

  webhook.guild.members.ban(executor.id, {
    reason: "Anti Webhook Delete"
  });

  const dmLoggingEnabled = await db.get(`${webhook.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await webhook.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Webhook Delete\n\n**Action Info:**\n﹒Channel :: ${webhook.name}\n﹒Channel ID :: ${webhook.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});


/* Anti Server Update */
client.on("guildUpdate", async (o, n) => {
  const auditLogs = await n.fetchAuditLogs({ limit: 3, type: "GUILD_UPDATE" });
  const logs = auditLogs.entries.first();
  const { executor, target } = logs;

  const trusted = await db.get(`${n.guild.id}_wl_${executor.id}`);
  const antinuke = await db.get(`${n.guild.id}_antinuke`);

  if (executor.id === o.ownerId) return;
  if (executor.id === client.user.id) return;
  if (antinuke !== true) return;
  if (trusted === true) return;

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
    const oldVanityCode = o.vanityURLCode;
    const newVanityCode = n.vanityURLCode;

    if (oldVanityCode !== newVanityCode) {
      phin({
        method: 'PATCH',
        url: `https://discord.com/api/v9/guilds/${n.id}/vanity-url`,
        json: true,
        headers: {
          "accept": "*/*",
          "Content-Type": 'application/json',
          "Authorization": `Bot ${bot.info.token}`
        },
        data: JSON.stringify({
          code: `${oldVanityCode}`
        }),
      }, (err, res, bod) => {
        if (err) console.log(chalk.red(`[-]: ${err}\n[+]: StatusCode: ${res.statusCode}`));
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

    for (x = 0; x <= 3; x++) {
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

  const dmLoggingEnabled = await db.get(`${n.guild.id}_dmlogs`);
  if (dmLoggingEnabled) {
    const owner = await o.guild.fetchOwner();
    let logs = new MessageEmbed()
      .setColor('#042134')
      .setDescription(`**_An Unauthorized Action Happened_**\n\n**Executor:**\n﹒Username :: ${executor.tag}\n﹒Action :: Server Update\n\n**Action Info:**\n﹒Server :: ${o.name}\n﹒Server ID :: ${n.id}\n\n**What I Did:**\n﹒Tried to ban the admin\n﹒Tried to recover the action`)
    owner.send({ embeds: [logs] })
  }
});

/* When Rate Limited */
client.on('rateLimit', (info) => {
  console.log(chalk.yellow(`${info}\n\n[!]; The bot is rate limited..`))
})

// #1
process.on("unhandledRejection", (reason, promise) => {
  console.log(chalk.red("[-]: " + reason))
});

// #2
process.on("uncaughtException", (err) => {
  console.log(chalk.red("[-]: " + err))
});

// #3
process.on('uncaughtExceptionMonitor', (err, origin) => {
  console.log(chalk.red("[-]: " + err));
});

// #4
process.on('multipleResolves', (type, promise, reason) => {
  console.log(chalk.red("[-]: ", type, promise, reason));
});


const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.send('Hello Express app!')
});

app.listen(port, () => {
  console.log('server started');
});