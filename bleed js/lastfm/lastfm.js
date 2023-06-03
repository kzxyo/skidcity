const Discord = require('discord.js')
const { default_prefix } = require("../../config.json");
const { color } = require('../../config.json')
const { approve } = require("../../emojis.json");
const { warn } = require("../../emojis.json");
const { deny } = require("../../emojis.json");


module.exports = {
    name: "lastfm",
    aliases: ["lf"],
    usage: "lastfm set [user]",
    category: "lastfm",

    run: (client, message, args) => {

        const low = require('lowdb')
        const FileSync = require('lowdb/adapters/FileSync')
        const adapter = new FileSync('fmuser.json');
        const db = low(adapter);
        const db2 = require('quick.db');
        let prefix = db2.get(`prefix_${message.guild.id}`);
        if (prefix === null) { prefix = default_prefix; };
        if (message.author.bot) return;

        if (!args[0]) return message.channel.send({ embed: {color: color, description: `${message.author}: To set your **Last.fm** account: \`${prefix}lastfm set <username>\``}})
        if (args[0].toLowerCase() == "set") {
            let fmUser = args[1];
            let period = args[2];
            const dbUser = db
                .get('users')
                .find({
                    userID: message.author.id
                })
                .value();
            if (dbUser) {
                fmUser = dbUser.lastFM;
                period = args[1];
            }   
            if (args.length === 3) {
                fmUser = args[1];
                period = args[2];
            }
            if (!args.join(" ").slice(3)) {
                let embed = new Discord.MessageEmbed()
                    .setColor("#efa23a")
                    .setDescription(`${warn} ${message.author}: You must provide a **Last.fm** username`)
                return message.channel.send(embed);
            }
            const existingUser = db
                .get('users')
                .find({
                    userID: message.author.id
                })
                .value();

            if (existingUser) {
                if (existingUser.lastFM === fmUser) {
                    return message.channel.send(
                        { embed: {color: "#efa23a", description: `${warn} ${message.author}: Your **Last.fm** profile is already set to **${fmUser}**`}}
                    );
                }
                existingUser.lastFM = fmUser;
                db.get('users')
                    .find({
                        userID: message.author.id
                    })
                    .assign({
                        lastFM: fmUser
                    })
                    .write();
                return message.channel.send(
                    { embed: {color: "#a3eb7b", description: `${approve} ${message.author}: Your **Last.fm** username has been updated to **${fmUser}**`}}
                );
            }
            db.get('users')
                .push({
                    userID: message.author.id,
                    lastFM: fmUser
                })
                .write();
            return message.channel.send({ embed: {color: "#a3eb7b", description: `${approve} ${message.author}: Your **Last.fm** username has been set to **${fmUser}**`}})
        } else if (args[0].toLowerCase() == "unlink") {
            const existingUser = db
                .get('users')
                .find({
                    userID: message.author.id
                })
                .value();

            if (existingUser) {
                db.get('users')
                    .remove({
                        userID: message.author.id
                    })
                    .write();
                return message.channel.send(
                    { embed: {color: "#a3eb7b", description: `${approve} ${message.author}: The **Last.fm** username **${existingUser.lastFM}** has been unlinked`}}
                );
            }
            return message.channel.send(
                { embed: {color: "#e74c3c", description: `${deny} ${message.author}: **Username** not found`}}
            );

        }
    }
}