const Command = require('../Command.js');
const {
    MessageEmbed
} = require('discord.js');
const Discord = require('discord.js')

module.exports = class GuildBannerCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'checkinvite',
            usage: `checkinvite <inviteCode>`,
            aliases: ["invitecheck", "checkinv", "findinvite"],
            subcommands: [`checkinvite`],
            description: `check an invite to any server provided, as long as you provide an invite code`,
            type: client.types.SEARCH,
        });
    }
    async run(message, args) {
        if (!args.length) {
            return this.help(message)
        }

        if (args.length > 11)
            return this.send_error(message, 1, "provided invite must be a \`code/vanity\` and not a \`link\`");
        if(args[0].toLowerCase().includes('http') || args[0].toLowerCase().includes('https')) {
            return this.send_error(message, 1, `You may not check **invite URL's**`)
        }
        if (args[0]) {

            let url = `https://discordapp.com/api/v8/invites/${args[0]}?with_counts=true`;
            let settings = {
                method: "Get"
            }
            fetch(url, settings)
                .then((res) => res.json())
                .then(async (res) => {
                    if(!res.guild) {
                        return this.send_error(message, 1, `There was no invite code found on discord named **${args[0]}**`)
                    }
                    const embed = new MessageEmbed()
                    .setAuthor(`${res.guild.name}`, `https://cdn.discordapp.com/icons/${res.guild.id}/${res.guild.icon}.webp?size=512`)
                    .setThumbnail(`https://cdn.discordapp.com/icons/${res.guild.id}/${res.guild.icon}.webp?size=512`)
                    .setTitle(`${res.guild.vanity_url_code ? 'Vanity:' : 'Invite'} ${res.guild.vanity_url_code ? res.guild.vanity_url_code : res.code}`)
                    .setDescription(`${res.description || '**No Description**'}`)
                    .addField(`**Inviter Info**`, `${res.inviter ? res.inviter.username+"#"+res.inviter.discriminator + `(${res.inviter.id})` : 'No Inviter (vanity)'}`)
                    .addField(`**Member Count**`, `${res.approximate_member_count}`)
                    .addField(`**Guild Icon**`, `[Click to view](https://cdn.discordapp.com/icons/${res.guild.id}/${res.guild.icon}.webp?size=512)`)
                    .addField(`**Guild Banner**`, `[Click to view](https://cdn.discordapp.com/banners/${res.guild.id}/${res.guild.banner}.webp?size=512)`)
                    .addField(`**Guild Features**`, `${res.guild.features.join(', ')}`)
                    .setColor(this.hex)
                    .setFooter(`Verification level: ${res.guild.verification_level}`)
                    message.channel.send({ embeds: [embed] })
                })
        }
    }
}