const Command = require('../Command.js');
const modes = ["delete", "add", "list", "removeall"];
const Discord = require('discord.js')
const db = require('quick.db')
const {
    MessageEmbed
} = require('discord.js');
const ReactionMenu = require('../ReactionMenu.js');

module.exports = class GivePointsCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'newfm',
            aliases: ['custom', 'customfm'],
            description: 'custom last.fm nowplaying commands',
            usage: 'newfm add <fm> \nnewfm delete <fm>\nnewfm list',
            type: client.types.OWNER,
            ownerOnly: true,
            subcommands: ['customcommand add kami']
        });
    }
    async run(message, args) {
        const prefix = this.db.get(`prefix_${message.guild.id}`) || ';'
        if (args[0].toLowerCase() == "add") {
            let name = args[1];
            if (!name) return this.send_error(message, 0, "Please include a customfm name");
            let commandObject = {};

            function random(length) {
                let string =
                    "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM";
                let secret = "";
                for (let i = length; i > 0; i--) {
                    const random = Math.floor(Math.random() * string.length);
                    const char = string.charAt(random);
                    string = string.replace(char, "");
                    secret += char;
                }
                return secret;
            }
            let id = random(20);
            commandObject.name = name;
            commandObject.id = id;
            let commandDescription;
            let exist = db.fetch(`customfm_${name}`);
            if (exist) {
                commandDescription = `customfm update\n \`Name:\` ${commandObject.name}`
                db.set(`customfm_${name}`, commandObject);
                return this.send_success(message, `${commandDescription}`);
            } else {
                commandDescription = `customfm creation\n \`Name:\` ${commandObject.name}`
                db.set(`customfm_${name}`, commandObject);
                return this.send_success(message, "\`" + commandObject.name + "\` was created as a custom fm", false)
            }
        } else if (args[0].toLowerCase() == "user") {
            let id = args[1]
            if(!id) return this.invalidArgs(message, `Provide an id to push as a customfm user`)
            db.set(`CustomfmUsers_${id}`, true)
            return this.send_success(message, `Customfm user updated: **${args[1]}**`)
        } else if (args[0].toLowerCase() == "delete") {
            let name = args[1];
            if (!name) return this.send_error(message, 0, "Please include a customfm");
            let exist = db.fetch(`customfm_${name}`);
            if (!exist) return this.send_error(message, 0, "That is not a customfm")
            db.delete(`customfm_${name}`)
            return this.send_success(message, `customfm \`${name}\` has been deleted`)
        } else if (args[0].toLowerCase() == "list") {
            let roles = db
                .all()
                .filter(data => data.ID.startsWith(`customfm_`))

            if (!roles.length) {
                return this.send_error(message, 0, "there are currently no customfms");

            }
            let num = 0
            let list = roles.map(f => `\`${++num}.\` **name:** - ${f.ID.slice(9)}`)
            const embed = new MessageEmbed()
                .setAuthor(`${message.author.tag}`, message.author.displayAvatarURL({
                    dynamic: true
                }))
            embed.setTitle(`Custom's List`)
                .setColor(message.guild.me.displayHexColor);
            if (list.length <= 10) {
                const range = (list.length == 1) ? '[1]' : `[1 - ${list.length}]`;
                message.channel.send(embed.setTitle(`Custom's List ${range}`).setDescription(list.join('\n')));
            } else {
                new ReactionMenu(message.client, message.channel, message.member, embed, list);
            }
        }
    }
};