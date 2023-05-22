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
  name: "autorole",
  description: "role new users ",
  aliases: [],
  usage: " ```YAML\n\n autorole {role_mention} ``` ",
  category: "moderation",
  guildOnly: false,
  args: false,
  permissions: {
    bot: [],
    user: [],
  },
  execute: async (message, args, client) => {
    if (talkedRecently.has(message.author.id)) {
      message.react(`⌛`);
    } else {
      let missperms = new MessageEmbed()
        .setDescription(`${xmark} You're missing \`MANAGE_GUILD\` permission`)
        .setColor(error);
      let trustedno = new MessageEmbed()
        .setDescription(`${xmark} Only trusted admins can use this command`)
        .setColor(error);

      if (!message.member.permissions.has([Permissions.FLAGS.MANAGE_GUILD]))
        return message.reply({ embeds: [missperms] });

      let trustedusers = db.get(`trustedusers_${message.guild.id}`);
      if (
        trustedusers &&
        trustedusers.find((find) => find.user == message.author.id) || message.guild.ownerId
        
      ) {
        let examplembed = new MessageEmbed()
          .setDescription(
            ` autorole <<role.id>> \n setup autorole to give roles to new members`
          )
          .setColor(color);
        if (args[0] === "none") {
          db.delete(`autorole_${message.guild.id}`);
          let embed = new MessageEmbed()
            .setDescription(`${checked} Removed Autorole`)
            .setColor(color);
          message.reply({ embeds: [embed] });
        }
        if (!args[0]) return message.reply({ embeds: [examplembed] });
        const role =
          message.mentions.roles.first() ||
          message.guild.roles.cache.get(args[1]) ||
          message.guild.roles.cache.find(
            (r) => r.name === args.slice(1).join(" ")
          ) ||
          message.guild.roles.cache.find((role) => role.name === args[1]) ||
          message.guild.roles.cache.find((role) => role.name.includes(args[1]));

        if (!role) {
          let embed = new MessageEmbed()
            .setDescription(`${xmark} couldn't find that role`)
            .setColor(error);
          message.reply({ embeds: [embed] });
        } else if (role) {
          console.log(role.perms)
          db.set(`autorole_${message.guild.id}`, role.id);
          let embed = new MessageEmbed()
            .setDescription(`${checked} Succesfully Set ${role} as autorole`)
            .setColor(color);
          message.reply({ embeds: [embed] });
        } else if (args[0] === "none") {
          db.delete(`autorole_${message.guild.id}`);
          let embed = new MessageEmbed()
            .setDescription(`${checked} Removed Autorole`)
            .setColor(color);
          message.reply({ embeds: [embed] });
        }
      } else return message.reply({ embeds: [trustedno] });

      // Adds the user to the set so that they can't talk for a minute
      talkedRecently.add(message.author.id);
      setTimeout(() => {
        // Removes the user from the set after a minute
        talkedRecently.delete(message.author.id);
      }, 3500);
    }
  },
};
