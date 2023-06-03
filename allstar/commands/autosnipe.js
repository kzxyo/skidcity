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
  name: "autosnipe",
  description: "auto snipes deletes message",
  aliases: [],
  usage: " ```YAML\n\n autosnipe [on/off] ``` ",
  category: "config",
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
          `<:allstarenabled:996521189986021386> Auto snipe is enabled `
        )
        .setColor(color);
      let checkdisabled = new MessageEmbed()
        .setDescription(
          `<:allstardisabled:996521221749481516>  Auto snipe is disabled `
        )
        .setColor(color);


      let aenabled = new MessageEmbed()
        .setDescription(`${checked} Auto snipe is now enabled`)
        .setColor(color);
      let missperms = new MessageEmbed()
        .setDescription(`${xmark} You're missing \`MANAGE_GUILD\` permission`)
        .setColor(error);

      let nukeable = new MessageEmbed()
        .setDescription(`${checked}  Auto snipe enabled`)
        .setColor(color);
      if (args[0] == "on") {
        if (!message.member.permissions.has([Permissions.FLAGS.MANAGE_GUILD]))
          return message.reply({ embeds: [missperms] });

        if ((await db.has(`autosniped_${message.guild.id}`)) === false) {
          await db.set(`autosniped_${message.guild.id}`, true);
          message.reply({ embeds: [nukeable] }).catch(() => {
            /*Ignore error*/
          });
        } else
          return message.reply({ embeds: [aenabled] }).catch(() => {
            /*Ignore error*/
          });
      } else if (args[0] == "off") {
        let disabled = new MessageEmbed()
          .setDescription(`${checked} Auto snipe disabled`)
          .setColor(color);
        let alreadydisabled = new MessageEmbed()
          .setDescription(`${xmark}  Auto snipe is already disabled `)
          .setColor(error);
        if ((await db.has(`autosniped_${message.guild.id}`)) === true) {
          await db.delete(`autosniped_${message.guild.id}`);
          message.reply({ embeds: [disabled] }).catch(() => {
            /*Ignore error*/
          });
        } else
          return message.reply({ embeds: [alreadydisabled] }).catch(() => {
            /*Ignore error*/
          });
      }
      if (!args[0]) {
        let antibot = db.get(`autosniped_${message.guild.id}`);
        if (antibot !== true) {
          return message.reply({ embeds: [checkdisabled] }).catch(() => {
            /*Ignore error*/
          });
        } else if (antibot === true) {
          return message.reply({ embeds: [checkenable] }).catch(() => {
            /*Ignore error*/
          });
        }
      }
    }

    talkedRecently.add(message.author.id);
    setTimeout(() => {
      // Removes the user from the set after a minute
      talkedRecently.delete(message.author.id);
    }, 3500);
  },
};
