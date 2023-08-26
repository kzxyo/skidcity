const Command = require('../../Structures/Base/command.js'), Discord = require('discord.js')

const os = require('os')

module.exports = class About extends Command {
    constructor (bot) {
        super (bot, 'about', {
            description : 'Show system information about blair.',
            aliases : [ 'botinfo', 'system', 'sys' ],
            module : 'Information'
        })
    }

    async execute (bot, message, args) {
        try {
            const members = bot.guilds.cache.reduce((total, guild) => total + guild.memberCount, 0)
            const channels = bot.channels.cache.size, textChannels = bot.channels.cache.filter((channel) => channel.type ===  0).size, voiceChannels = bot.channels.cache.filter((channel) => channel.type ===  2).size
            const guilds = bot.guilds.cache.size

            const cpus = os.cpus();
const cpu = cpus[0];

const total = Object.values(cpu.times).reduce(
    (acc, tv) => acc + tv, 0
);

const usage = process.cpuUsage();
const currentCPUUsage = (usage.user + usage.system) * 1000;

const perc = (currentCPUUsage / total * 100).toFixed(2);
            message.channel.send({
                embeds : [
                    new Discord.EmbedBuilder({
                        author : {
                            name : 'blair',
                            iconURL : bot.user.displayAvatarURL()
                        },
                        description : `Developed by **${bot.owner.username}**\n**Memory**: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024 * 100) / 100}MB, **CPU**: ${perc}%`,
                        fields : [
                            {
                                name : 'Members',
                                value : `**Total**: ${members.toLocaleString()}\n**Unique**: ${bot.users.cache.size.toLocaleString()}`,
                                inline : true
                            },
                            {
                                name : 'Channels',
                                value : `**Total**: ${channels.toLocaleString()}\n**Text**: ${textChannels.toLocaleString()}\n**Voice**: ${voiceChannels.toLocaleString()}`,
                                inline : true
                            },
                            {
                                name : 'Client',
                                value : `**Servers**: ${guilds.toLocaleString()}\n**Commands**: ${(bot.commands.size + bot.subCommands.size).toLocaleString()}`,
                                inline : true
                            }
                        ]
                    }).setColor(bot.colors.neutral)
                ]
            })
        } catch (error) {
            return bot.error(
                message, 'about', error
            )
        }
    }
}