const { MessageEmbed, Permissions } = require("discord.js");
const db = require('quick.db')
const {
  default_prefix,
  color,
  error,
  owner,
  checked,
  xmark,
} = require("../config.json");
const talkedRecently = new Set();
module.exports = {
  name: "antialt",
  description: "kicks new accounts possibly alt accounts",
  aliases: [],
  usage: "\```YAML\n\n antialt [on/off] \```",
  category: "security",
  guildOnly: false,
  args: false,
  permissions: {
    bot: [],
    user: [],
  },
  execute: async (message, args, client) => {
    let emoji = `<:887705796476018688:989122635705233418> `;
    if (talkedRecently.has(message.author.id)) {
      message.react(`⌛`);
    } else {
      let checkenable = new MessageEmbed()
        .setDescription(
          `<:allstarenabled:996521189986021386> Anti Alt Is Enabled `
        )
        .setThumbnail(
          `https://cdn.discordapp.com/attachments/991601306747813978/996704762110148688/IconServerSecurity_1.gif`
        )
        .setColor(color);
      let checkdisabled = new MessageEmbed()
        .setDescription(
          `<:allstardisabled:996521221749481516>  Anti Alt Is Disabled `
        )
        .setThumbnail(
          `https://cdn.discordapp.com/attachments/991601306747813978/996704762110148688/IconServerSecurity_1.gif`
        )
        .setColor(color);
      let onlyown = new MessageEmbed()
        .setDescription(`${xmark} Only server owner can use this command`)
        .setColor(error);

      const authorized = [message.guild.ownerId, owner];
      //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});
      if (!authorized.includes(message.author.id))
        return message.reply({ embeds: [onlyown] }).catch(() => {
          /*Ignore error*/
        });

      let aenabled = new MessageEmbed()
        .setDescription(`${checked} Anti Alt is now enabled`)
        .setColor(color);
      let missperms = new MessageEmbed()
        .setDescription(`${xmark}  You're missing \`MANAGE_GUILD\` permission`)
        .setColor(error);

      let nukeable = new MessageEmbed()
        .setDescription(`${checked}  Anti Alt enabled`)
        .setColor(color);
      if (args[0] == "on") {
        if (!authorized.includes(message.author.id))
          return message.reply({ embeds: [onlyown] });
        if ((await db.has(`antiraid_${message.guild.id}`)) === false) {
          await db.set(`antiraid_${message.guild.id}`, true);
          message.reply({ embeds: [nukeable] }).catch(() => {
            /*Ignore error*/
          });
        } else
          return message.reply({ embeds: [aenabled] }).catch(() => {
            /*Ignore error*/
          });
      } else if (args[0] == "off") {
        let disabled = new MessageEmbed()
          .setDescription(`${checked}  Anti Alt is now disabled`)
          .setColor(color);
        let alreadydisabled = new MessageEmbed()
          .setDescription(`${xmark}  Anti Alt is disabled`)
          .setColor(error);
        if ((await db.has(`antiraid_${message.guild.id}`)) === true) {
          await db.delete(`antiraid_${message.guild.id}`);
          message.reply({ embeds: [disabled] }).catch(() => {
            /*Ignore error*/
          });
        } else
          return message.reply({ embeds: [alreadydisabled] }).catch(() => {
            /*Ignore error*/
          });
      }
      if (!args[0]) {
        let antibot = db.get(`antiraid_${message.guild.id}`);
        if (antibot !== true) {
          return message.reply({ embeds: [checkdisabled] }).catch(() => {
            /*Ignore error*/
          });
        } else if (antibot === true) {
          return message.reply({ embeds: [checkenable] }).catch(() => {
            /*Ignore error*/
          });
        }
      } else if (args[0] == "info") {
        let embed11 = new MessageEmbed()
          .setDescription(
            `<:allstaruser:998562258210803793>  Anti Alt \n <:allstar:1001031487103193108> antialt [on/off] info :\`kicks every alt account if enabled \``
          )

          .setColor(color);
        message.reply({ embeds: [embed11] }).catch(() => {
          /*Ignore error*/
        });
      }
    }

    talkedRecently.add(message.author.id);
    setTimeout(() => {
      // Removes the user from the set after a minute
      talkedRecently.delete(message.author.id);
    }, 3500);
  },
};
