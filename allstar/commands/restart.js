
const { MessageEmbed } = require('discord.js');
const { owner } = require("../config.json")
module.exports = {
    name: 'restart',
    description: 'Restart the bot via PM2.',
    aliases: ["reboot"],
    usage: 'restart',
    guildOnly: false,
    args: false,
    permissions: {
        bot: [],
        user: [],
    },
    execute: async (message, args, client) => {
        var permissionDenied = new MessageEmbed()
            .setColor("#8B0000")
            .setAuthor({ name: "Error Occured" })
            .setTitle("Permission Denied")
            .setDescription("You do not have permission to use this command. This command is only available to the bot owner.")
            .setTimestamp()
            .setFooter({
                text: `${client.user.username}`,
                iconURL: client.user.displayAvatarURL()
            });
        var loadingEmbed = new MessageEmbed()
            .setColor("#FFFFFF")
            .setTitle("Restarting Bot <a:vile_loading:1045004235915411536>")
            .setDescription("Please wait while the bot is being restarted. This may take a few minutes.")
            .setTimestamp()
            .setFooter({
                text: `${client.user.username}`,
                iconURL: client.user.displayAvatarURL()
            });
        if (owner.toString() !== message.author.id.toString() && message.author.id.toString() !== "461914901624127489") return message.reply({ embeds: [permissionDenied] })
        var msg = await message.reply({ embeds: [loadingEmbed] })
        // execute a child command asynchonously
        const { exec } = require('child_process');
        await exec(`echo '1 ${message.guild.id} ${message.channel.id} ${msg.id}' > /home/allstar/allstar/rstrt-stat-indtr.num`)
        await exec("pm2 restart 0")

    }
};
