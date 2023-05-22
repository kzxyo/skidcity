const { MessageEmbed,Permissions } = require("discord.js");
const {
  default_prefix,
  color,
  error,
  owner,
  checked,
  xmark,
} = require("../config.json");
const db = require('quick.db')
const talkedRecently = new Set();
module.exports = {
  name: "antilink",
  description: "protects against links",
  aliases: [],
  usage:
    " ```YAML\n\n antilink [on/off], \n antilink whitelist, \n antilink blacklist, \n antilink whitelisted, ``` ",
    category: "security",
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



      let aenabled = new MessageEmbed()
        .setDescription(`${checked} Anti link is now enabled`)
        .setColor(color);
      let missperms = new MessageEmbed()
        .setDescription(`${xmark} You're missing \`MANAGE_GUILD\` permission `)
        .setColor(error);

      let nukeable = new MessageEmbed()
        .setDescription(`${checked}  Anti link is Enabled`)
        .setColor(color);

   
        if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_GUILD])) return message.reply({ embeds:[missperms]});

       if (args[0] === "off") {
        let disabled = new MessageEmbed()
          .setDescription(`${checked}  Anti link is now disabled`)
          .setColor(color);

        if ((await db.has(`antilink_${message.guild.id}`)) === true) {
          await db.delete(`antilink_${message.guild.id}`);
          message.reply({ embeds: [disabled] }).catch(() => {
            /*Ignore error*/
          });
        }
      } else if (args[0] === "on") {
        if ((await db.has(`antilink_${message.guild.id}`)) === false) {
          await db.set(`antilink_${message.guild.id}`, true);
          message.reply({ embeds: [nukeable] }).catch(() => {
            /*Ignore error*/
          });
        } else
          return message.reply({ embeds: [aenabled] }).catch(() => {
            /*Ignore error*/
          });
      } else if (args[0] == "info") {

        let embed11 = new MessageEmbed()

          .setDescription(
            `<:allstarsecurity:996512639666618518>  Allstar anti link \n <:allstar:1001031487103193108> antilink on - toggles antilink event on \n <:allstar:1001031487103193108> antilink off - toggles antilink event off \n <:allstar:1001031487103193108> antilink whitelist \n <:allstar:1001031487103193108> antilink blacklist \n <:allstar:1001031487103193108> antilink whitelisted`
          )
          .setThumbnail(client.user.displayAvatarURL())
          .setColor(color);

        message.reply({ embeds: [embed11] }).catch(() => {
          /*Ignore error*/
        });
      }
      if (!args[0]) {
        let checkenable = new MessageEmbed()

          .setDescription(
            `<:allstarenabled:996521189986021386> Anti link is enabled  \n Usage : \n <:allstar:1001031487103193108> antilink [on/off] \n  antilink whitelist \n <:allstar:1001031487103193108> antilink blacklist \n <:allstar:1001031487103193108> antilink whitelisted`
          )
          .setColor(color);
        let checkdisabled = new MessageEmbed()
          .setDescription(
            `<:allstardisabled:996521221749481516>  Anti link is disabled \n Usage : \n <:allstar:1001031487103193108> antilink [on/off] \n  antilink whitelist \n <:allstar:1001031487103193108> antilink blacklist \n <:allstar:1001031487103193108> antilink whitelisted`
          )
          .setColor(color);
        let antinuke = db.get(`antilink_${message.guild.id}`);
        if (antinuke !== true) {
          return message.reply({ embeds: [checkdisabled] }).catch(() => {
            /*Ignore error*/
          });
        } else if (antinuke === true) {
          return message.reply({ embeds: [checkenable] }).catch(() => {
            /*Ignore error*/
          });
        }
      } else if (args[0] === "whitelist") {
        let antinuke = db.get(`antilink_${message.guild.id}`);

                let missperms = new MessageEmbed()
        .setDescription(`${xmark}  You're missing \`MANAGE_GUILD\` permission`)
        .setColor(error)
        if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_GUILD])) return message.reply({ embeds:[missperms]});
        
        if (antinuke !== true) {
          return message.reply({embeds:[{description:`${xmark} Enable antilink first`,color:error}]});
        }
        let user =
          message.mentions.users.first() ||
          message.guild.members.cache.get(args[1]);
        if (!user) {
          let usermention = new MessageEmbed()
            .setDescription(
              `
            ${xmark}  Mention user to whitelist
            `
            )
            .setColor(error);

          return message.reply({
            embeds: [usermention],
          });
        }
        let trustedusers = db.get(`linktrusted_${message.guild.id}`);
        if (trustedusers && trustedusers.find((find) => find.user == user.id)) {
          let trust = new MessageEmbed()
            .setColor(error)
            .setDescription(`${xmark}  That user is already whitelisted`);
          return message.reply({ embeds: [trust] });
        }
        let data = {
          user: user.id,
        };
        db.push(`linktrusted_${message.guild.id}`, data);
        let added = new MessageEmbed()
          .setDescription(
            `
        ${checked}  Anti link Whitelisted ${user}
        `
          )
          .setColor(color);

        return message.reply({
          embeds: [added],
        });
      } else if (args[0] === "blacklist") {
        let antinuke = db.get(`antilink_${message.guild.id}`);
                let missperms = new MessageEmbed()
        .setDescription(`${xmark}  You're missing \`MANAGE_GUILD\` permission`)
        .setColor(error)
        if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_GUILD])) return message.reply({ embeds:[missperms]});
        if (antinuke !== true) {
          return message.reply({embeds:[{description:`${xmark} Enable antilink first`,color:error}]});
        }
        let user =
          (await message.mentions.members.first()) ||
          message.guild.members.cache.get(args[1]) ||
          args[0];
        if (!user) {
          let usermention = new MessageEmbed()
            .setDescription(`${xmark}  Mention a user/ID`)
            .setColor(error);
          return message.reply({
            embeds: [usermention],
          });
        }

        let database = db.get(`linktrusted_${message.guild.id}`);
        if (database) {
          let data = database.find((x) => x.user === user.id);
          let unabletofind = new MessageEmbed()
            .setDescription(
              `${xmark}  Could not find that user in the database`
            )
            .setColor(error);
          if (!data) return message.reply({ embeds: [unabletofind] });

          let value = database.indexOf(data);
          delete database[value];

          var filter = database.filter((x) => {
            return x != null && x != "";
          });

          db.set(`linktrusted_${message.guild.id}`, filter);
          let deleted = new MessageEmbed()
            .setDescription(`${checked} Removed ${user} From Vanity Whitelist.`)
            .setColor(color);

          return message.reply({
            embeds: [deleted],
          });
        } else {
          let notrust = new MessageEmbed()
            .setDescription(`${xmark}  That user is not whitelisted`)
            .setColor(error);
          message.reply({ embeds: [notrust] });
        }
      } else if (args[0] === "whitelisted") {
        let errors = new MessageEmbed()
          .setDescription(`${xmark} There are no whitelisted users`)
          .setColor(error);

                let missperms = new MessageEmbed()
        .setDescription(`${xmark}  You're missing \`MANAGE_GUILD\` permission`)
        .setColor(error)
        if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_GUILD])) return message.reply({ embeds:[missperms]});

        let guild = message.guild.iconURL();

        let wordlist = new MessageEmbed();
        let database = db.get(`linktrusted_${message.guild.id}`);
        if (database == null)
          return message
            .reply({
              content: `${xmark} there are no antilink whitelisted users`,
            })
            .catch(() => {
              /*Ignore error*/
            });
        if (database && database.length) {
          let arrayv = [];

          database.forEach((m) => {
            arrayv.push(`<@${m.user}> - ${m.user}`);
          });
          wordlist.setDescription(message.guild.name);
          wordlist.addField("Anti link whitelists", `>  ${arrayv.join("\n> ")}`);
          wordlist.setThumbnail(message.guild.iconURL({ dynamic: true }));
          wordlist.setColor(color);
        }

        // if(database == null) return (message.reply({content:`<:allstarwarn:996517869791748199> there are no whitelisted users`})).catch(() => {/*Ignore error*/});

        message.reply({ embeds: [wordlist] }).catch(() => {
          message.reply({ embeds: [errors] });
        });
      }

      // Adds the user to the set so that they can't talk for a minute
      talkedRecently.add(message.author.id);
      setTimeout(() => {
        // Removes the user from the set after a minute
        talkedRecently.delete(message.author.id);
      }, 3500);
    }
  },
};
