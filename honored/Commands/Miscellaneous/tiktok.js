const { fetch } = require('undici');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'tiktok',
        aliases: ['tt'],
        description: 'Get information on a TikTok profile',
        syntax: 'tiktok [username]',
        example: 'tiktok cjm',
        permissions: 'N/A',
        parameters: 'username',
        module: 'miscellaneous'
    },
    run: async (session, message, args, prefix) => {
        try {
            if (!args.length) {
                return displayCommandInfo(module.exports, session, message);
            }

            const username = String(args[0]).toLowerCase();
            const response = await fetch(`https://www.tikwm.com/api/user/info?unique_id=${username}`, {
                method: 'POST'
            });
            const data = await response.json();

            if (!data.data) {
                return session.warn(message, `Profile [**${username}**](https://www.tiktok.com/@${username}) doesn't exist`);
            }

            const { user, stats } = data.data;

            const embed = new MessageEmbed()
                .setTitle(`${user.uniqueId !== user.nickname ? `${user.nickname} (@${user.uniqueId})` : `${user.uniqueId}`} ${user.privateAccount ? ':lock:' : user.verified ? ':ballot_box_with_check:' : ''}`)
                .setURL(`https://www.tiktok.com/@${user.uniqueId}`)
                .setDescription(user.signature)
                .addFields(
                    { name: 'Likes', value: stats.heartCount.toLocaleString(), inline: true },
                    { name: 'Followers', value: stats.followerCount.toLocaleString(), inline: true },
                    { name: 'Following', value: stats.followingCount.toLocaleString(), inline: true }
                )
                .setThumbnail(user.avatarLarger)
                .setColor(session.color);

            message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log("Error:", error.message)
            const errorEmbed = new MessageEmbed()
            .setColor(session.warn)
            .setDescription(`${session.mark} ${message.author}: API returned an errorr`);
            return message.channel.send({ embeds: [errorEmbed] });
        }
    }
};
