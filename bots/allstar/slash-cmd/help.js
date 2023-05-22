const { SlashCommandBuilder } = require('@discordjs/builders');
const { MessageEmbed } = require('discord.js');
var fs = require('fs');
const { normalize } = require('path');
const { description } = require('../commands/usage');
module.exports.name = "help";
module.exports.slashCmd = new SlashCommandBuilder()
    .setName('help')
    .setDescription('Displays useful information about each individual command included with Allstar.')
module.exports.runCmd = async (client, interaction, GeneralData) => {
    var requireAsync = async function (module) {
        return new Promise(function (resolve, reject) {
            fs.readFile(module, { encoding: 'utf8' }, function (err, data) {
                var module = {
                    exports: {}
                };
                var code = '(function (module) {' + data + '})(module)';
                eval(code);
                resolve(module)
            });
        })
    };
    var categories = [
        "utility",
        "lastfm",
        "security",
        "moderation",
        "config",
        "image",
        "information",
        "welcome/goodbye",
        "joindm"
    ]
    var category_info_embeds = [
        [], [], [], [], [], [], [], [], []
    ];
    for (var kv of Array.from(client.commands)) {
        var len = Array.from(client.commands).length;
        var k = kv[0],
            v = kv[1];
        var category = categories.indexOf(v.category);
        if (category === -1) continue;
        category = categories[category];
        if (!v.name) continue;
        var description = (v.description === undefined || v.description === "") ? "N/A" : v.description;
        var usage = (v.usage === undefined || v.usage === "") ? "N/A" : v.usage;
        var aliases = (v.aliases === undefined || v.aliases?.length === 0) ? "N/A" : v.aliases.join(", ");
        console.log(v.name === "welcome")
        category_info_embeds[categories.indexOf(category)].push(
            new MessageEmbed()
                .setColor("#FF0000")
                .setAuthor({ name: "Help Menu" })
                .setTitle(`**${category}** | Commands`)
                .setDescription(`Command Description: ${description}`)
                .addFields(
                    { name: "Command Name: ", value: `${v.name}`, inline: true },
                    { name: "Command Aliases: ", value: `${aliases}`, inline: true },
                    { name: "Command Usage: ", value: `${usage}`, inline: true }
                )
                .setTimestamp()
                .setFooter({
                    text: `${client.user.username}`,
                    iconURL: client.user.displayAvatarURL()
                })
        )
    }
    var options = [
        {
            "name": "Configuration",
            "description": "Here you can find commands that allow you to configure Allstar to your liking. You can change the prefix, enable certain features, and more.",
            "number_of_embeds": category_info_embeds[4].length + 1,
            "emoji": "1010885871773433866"
        },
        {
            "name": "Image",
            "description": "A fun little collection of commands related to the manipulation of images, usually in a meme-like fashion.",
            "number_of_embeds": category_info_embeds[5].length + 1,
            "emoji": "996512771892060160"
        },
        {
            "name": "Information",
            "description": "Basic commands that provide information about a user, server, the bot, or other things.",
            "number_of_embeds": category_info_embeds[6].length + 1,
            "emoji": "997234551568994324"
        },
        {
            "name": "JoinDM",
            "description": "A feature that allows you to send a message to a user when they join your server. This is a great way to welcome new members.",
            "number_of_embeds": category_info_embeds[8].length + 1,
            "emoji": "1010885882678620193"
        },
        {
            "name": "LastFM",
            "description": "Commands that allow you to interact with the LastFM API. You can get information about your favorite artists, albums, and more.",
            "number_of_embeds": category_info_embeds[1].length + 1,
            "emoji": "1042492189600657508"
        },
        {
            "name": "Moderation",
            "description": "Both basic & advanced moderation commands that allow you to moderate your server. You can kick, ban, mute, and more to protect your server.",
            "number_of_embeds": category_info_embeds[3].length + 1,
            "emoji": "1033522274151702640"
        },
        {
            "name": "Security",
            "description": "A suite of commands that allow you to protect your server from malicious users. You can enable a verification system (AntiNuke), and more.",
            "number_of_embeds": category_info_embeds[2].length + 1,
            "emoji": "1010885860801126461"
        },
        {
            "name": "Utility",
            "description": "Small utility commands to obtain basic info about users or bots.",
            "number_of_embeds": category_info_embeds[0].length + 1,
            "emoji": "1010885871119106058"
        },
        {
            "name": "Welcome/Goodbye",
            "description": "Configure a welcome or goodbye message to be sent when a user joins or leaves your server.",
            "number_of_embeds": category_info_embeds[7].length + 1,
            "emoji": "1010885882678620193"
        }
    ]
    function createLandingEmbed(category, stats) {
        if (options.filter(x => x.name == category)[0] === undefined) console.log(category)
        stats[2] = stats[0]
        return new MessageEmbed()
            .setColor("#FFFFFF")
            .setAuthor({ name: "Help Menu" })
            .setTitle(`**${category}** | Commands`)
            .setDescription(`${options.filter(x => x.name == category)[0].description}`)
            .addFields(
                { name: "Category Name: ", value: `${category}`, inline: true },
                { name: "Total Commands: ", value: `${stats[0]} Normal / ${stats[1]} Slash (${stats[2]} Total)`, inline: true }
            )
            .setTimestamp()
            .setFooter({
                text: `${client.user.username}`,
                iconURL: client.user.displayAvatarURL()
            })
    }
    var Paginator = await requireAsync("/home/allstar/allstar/Paginator.js")
    Paginator = Paginator.exports.MultiMenuPaginator
    var paginator = new Paginator(client, GeneralData.message, [
        [createLandingEmbed("Configuration", [category_info_embeds[4].length, 0, 0])].concat(category_info_embeds[4]),
        [createLandingEmbed("Image", [category_info_embeds[5].length, 0, 0])].concat(category_info_embeds[5]),
        [createLandingEmbed("Information", [category_info_embeds[6].length, 0, 0])].concat(category_info_embeds[6]),
        [createLandingEmbed("JoinDM", [category_info_embeds[8].length, 0, 0])].concat(category_info_embeds[8]),
        [createLandingEmbed("LastFM", [category_info_embeds[1].length, 0, 0])].concat(category_info_embeds[1]),
        [createLandingEmbed("Moderation", [category_info_embeds[3].length, 0, 0])].concat(category_info_embeds[3]),
        [createLandingEmbed("Security", [category_info_embeds[2].length, 0, 0])].concat(category_info_embeds[2]),
        [createLandingEmbed("Utility", [category_info_embeds[0].length, 0, 0])].concat(category_info_embeds[0]),
        [createLandingEmbed("Welcome/Goodbye", [category_info_embeds[7].length, 0, 0])].concat(category_info_embeds[7])
    ], options);
    paginator.setTimeout(60000 * 10)
    paginator.setAuthors([GeneralData.user_id])
    paginator.on("Error", function (error) {
        console.log(error)
    })
    paginator.construct()
}