const { SlashCommandBuilder } = require('@discordjs/builders');
const { MessageEmbed } = require("discord.js")
const { exec } = require('child_process');
var memStat = require('mem-stat');
var fs = require("fs")
const { MessageActionRow, MessageButton } = require('discord.js');
module.exports.name = "jsk";
module.exports.slashCmd = new SlashCommandBuilder()
    .setName('jsk')
    .setDescription('Evaluates an action resembling that of the JSK module built with Python.')
    .addSubcommand(subcommand =>
        subcommand
            .setName('info')
            .setDescription('Info about the current installation of JSK.'))
    .addSubcommand(subcommand =>
        subcommand
            .setName('shutdown')
            .setDescription('Shuts down the bot.'))
    .addSubcommand(subcommand =>
        subcommand
            .setName('exit-node')
            .setDescription('Shuts down the bot & exits the current node process.'))
    .addSubcommand(subcommand =>
        subcommand
            .setName('reload-all')
            .setDescription('Reloads all modules (Soft Restart).'))
    .addSubcommand(subcommand =>
        subcommand
            .setName('reload')
            .setDescription('Reload a command or event (module).')
            .addStringOption(option =>
                option.setName('type')
                    .setDescription('The type of module you want to reload.')
                    .setRequired(true)
                    .addChoices(
                        { name: 'Command', value: 'mod_reload_cmd' },
                        { name: 'Slash Command', value: 'mod_reload_slshcmd' }
                    ))
            .addStringOption(option => option.setName('module').setDescription('Please enter which module you want to reload.').setRequired(true))

    )
module.exports.runCmd = async (client, interaction, GeneralData) => {
    if (!["461914901624127489", "979978940707930143", "812126383077457921"].includes(GeneralData.user_id.toString())) return await GeneralData.message.edit({
        embeds: [new MessageEmbed()
            .setColor("#8B0000")
            .setAuthor({ name: "An Error Occured" })
            .setTitle("Permission Denied")
            .setDescription("JSK is an owner-only command.")
            .setTimestamp()
            .setFooter({
                text: `${client.user.username}`,
                iconURL: client.user.displayAvatarURL()
            })], ephemeral: true
    })
    if (interaction.options._subcommand === "info") {
        Number.prototype.formatBytes = function () {
            var units = ['B', 'KB', 'MB', 'GB', 'TB'],
                bytes = this,
                i;

            for (i = 0; bytes >= 1024 && i < 4; i++) {
                bytes /= 1024;
            }

            return bytes.toFixed(2) + " " + units[i];
        }
        var name = "JishakuNJS"
        var version = "v0.0.1"
        var library = "discord.js"
        var library_version = require("../package.json").dependencies["discord.js"].replace("^", "")
        var runner = "Node.js"
        var runner_version = process.version.replace("v", "")
        var runner_release_date = "2021-07-05"
        async function getGCCVersion() {
            return new Promise(async function (resolve, reject) {
                await exec("gcc -v 2>&1 | tail -n 1", async (err, stdout, stderr) => {
                    if (err) {

                    }
                    var output = stdout.toString();
                    resolve({
                        "version.1": output.split(" ")[2],
                    })
                })
            })
        }
        var versionH = await getGCCVersion()
        var vs1 = versionH["version.1"]
        var platform = process.platform.toString()
        var loaded_on = Math.floor(client.loadedOn / 1000)
        var ready_on = Math.floor(client.readyOn / 1000)
        async function getUsedMemory() {
            return new Promise(async function (resolve, reject) {
                await exec("pm2 ls | grep allstar", async (err, stdout, stderr) => {
                    if (err) {

                    }
                    var output = stdout.toString();
                    var mem = output.split("│")[11]
                    if (!mem.toString().includes(".")) mem = "Unknown"
                    resolve(mem.toString().replace(" ", "").replace("  ", ""))
                })
            })
        }
        var memUsage = (await getUsedMemory()).toString().replace("mb", " MB").replace("gb", " GB")
        var total_system_used = (memStat.total("GiB") - memStat.free("GiB")).toFixed(2)
        var pid = process.pid
        var command = "node"
        async function getAmountOfThreads() {
            return new Promise(async function (resolve, reject) {
                await exec(`find /proc/${pid}/task -maxdepth 1 -type d -print | wc -l`, async (err, stdout, stderr) => {
                    if (err) {

                    }
                    var output = stdout.toString();
                    resolve(output)
                })
            })
        }
        var threads = await getAmountOfThreads()
        var unique_mem = (process.memoryUsage().heapTotal).formatBytes()
        if (client.cluster?.id !== null && client.cluster?.id !== undefined) {
            global.smsg_tmp = await client.cluster.fetchClientValues('guilds.cache.size')
            global.smsg_tmp_2 = global.smsg_tmp.reduce((acc, guildCount) => acc + guildCount, 0)
            global.smsg_tmp3 = 0
            var aom = await client.cluster.broadcastEval((c) => c.guilds.cache.map((guild) => 
            guild.memberCount));
            aom = aom[0].reduce((partialSum, a) => partialSum + a, 0)
            console.log(aom)
            global.smsg_tmp3 = aom
        }
        var msg_begin = (client.cluster?.id === undefined) ? `This bot is not sharded and can see ${client.guilds.cache.size} guild(s) and ${client.guilds.cache.reduce((a, g) => a + g.memberCount, 0)} user(s).` : `This bot is automatically sharded (Shards ${GeneralData.message?.guild?.shardId} Of ${global.smsg_tmp?.length}) and can see ${global.smsg_tmp_2} guild(s) and ${global.smsg_tmp3} user(s).`
        await interaction.editReply({
             embeds: [{description:`${name} ${version}, ${library} \`${library_version}\`, \`${runner} ${runner_version} (main, ${runner_release_date}) [GCC ${vs1}]\` on \`${platform}\`
Bot was started <t:${loaded_on}:R>, module was loaded <t:${ready_on}:R>.
            

Using ${memUsage} physical memory and ${total_system_used} GiB virtual memory, ${unique_mem} of which unique to this process.
Running on PID ${pid} (\`${command}\`) with ${threads} thread(s).

${msg_begin}
Message cache capped at 1000, presences intent is enabled, members intent is enabled, and message content intent is enabled.
Average websocket latency: ${Math.round(client.ws.ping)}ms`,color:"FFFFFF", ephemeral: false
    }]})
    }
    if (interaction.options._subcommand === "reload") {
        const module_type = interaction.options.getString('type');
        const module_arg = interaction.options.getString('module');
        if (module_type === undefined || module_type === null || module_arg === undefined || module_arg === null) if (!module) return await GeneralData.message.edit({
            embeds: [new MessageEmbed()
                .setColor("#8B0000")
                .setAuthor({ name: "An Error Occured" })
                .setTitle("Slash Command Failed")
                .setDescription(`While attempting to reload the module requested, the slash command recieved an invalid request.`)
                .setTimestamp()
                .setFooter({
                    text: `${client.user.username}`,
                    iconURL: client.user.displayAvatarURL()
                })], ephemeral: false
        })
        if (!["mod_reload_cmd", "mod_reload_slshcmd"].includes(module_type.toString())) return await GeneralData.message.edit({
            embeds: [new MessageEmbed()
                .setColor("#8B0000")
                .setAuthor({ name: "An Error Occured" })
                .setTitle("Module Type Not Found")
                .setDescription(`The module type ${module_type.toString()} was not found or is not registered.`)
                .setTimestamp()
                .setFooter({
                    text: `${client.user.username}`,
                    iconURL: client.user.displayAvatarURL()
                })], ephemeral: false
        })
        var requireAsync = function (module, callback) {
            fs.readFile(module, { encoding: 'utf8' }, function (err, data) {
                var module = {
                    exports: {}
                };
                var code = '(function (module) {' + data + '})(module)';
                eval(code);
                callback(null, module);
            });
        }
        if (module_type.toString() === "mod_reload_cmd") {
            var module = client.commands.get(module_arg.toString().toLowerCase())
            if (!module) return await GeneralData.message.edit({
                embeds: [new MessageEmbed()
                    .setColor("#8B0000")
                    .setAuthor({ name: "An Error Occured" })
                    .setTitle("Module Not Found")
                    .setDescription(`The module ${module_arg.toString().toLowerCase()} was not found or is not registered.`)
                    .setTimestamp()
                    .setFooter({
                        text: `${client.user.username}`,
                        iconURL: client.user.displayAvatarURL()
                    })], ephemeral: false
            })
            var deleted = client.commands.delete(module_arg.toString().toLowerCase())
            if (!deleted) return await GeneralData.message.edit({
                embeds: [new MessageEmbed()
                    .setColor("#8B0000")
                    .setAuthor({ name: "An Error Occured" })
                    .setTitle("Module Not Deleted")
                    .setDescription(`The module ${module_arg.toString().toLowerCase()} could not be deleted for an unkonwn reason.`)
                    .setTimestamp()
                    .setFooter({
                        text: `${client.user.username}`,
                        iconURL: client.user.displayAvatarURL()
                    })], ephemeral: false
            })
            requireAsync(`/home/allstar/allstar/commands/${module_arg.toString().toLowerCase()}.js`, function (err, module) {
                if (err) throw err;
                client.commands.set(module_arg.toString().toLowerCase(), module.exports)
            })
            await GeneralData.message.edit({
                embeds: [new MessageEmbed()
                    .setColor("#008B00")
                    .setAuthor({ name: "JishakuNJS" })
                    .setTitle("Module Reloaded")
                    .setDescription(`The module ${module_arg.toString()} [Type: Command] was reloaded successfully.`)
                    .setTimestamp()
                    .setFooter({
                        text: `${client.user.username}`,
                        iconURL: client.user.displayAvatarURL()
                    })], ephemeral: false
            })
        }

        if (module_type.toString() === "mod_reload_slshcmd") {
            var module = client.slash.get(module_arg.toString().toLowerCase())
            if (!module) return await GeneralData.message.edit({
                embeds: [new MessageEmbed()
                    .setColor("#8B0000")
                    .setAuthor({ name: "An Error Occured" })
                    .setTitle("Module Not Found")
                    .setDescription(`The module ${module_arg.toString().toLowerCase()} was not found or is not registered.`)
                    .setTimestamp()
                    .setFooter({
                        text: `${client.user.username}`,
                        iconURL: client.user.displayAvatarURL()
                    })], ephemeral: false
            })
            var deleted = client.slash.delete(module_arg.toString().toLowerCase())
            if (!deleted) return await GeneralData.message.edit({
                embeds: [new MessageEmbed()
                    .setColor("#8B0000")
                    .setAuthor({ name: "An Error Occured" })
                    .setTitle("Module Not Deleted")
                    .setDescription(`The module ${module_arg.toString().toLowerCase()} could not be deleted for an unkonwn reason.`)
                    .setTimestamp()
                    .setFooter({
                        text: `${client.user.username}`,
                        iconURL: client.user.displayAvatarURL()
                    })], ephemeral: false
            })
            requireAsync(`/home/allstar/allstar/slash-cmd/${module_arg.toString().toLowerCase()}.js`, function (err, module) {
                if (err) throw err;
                client.slash.set(module_arg.toString().toLowerCase(), module.exports)
            })
            await GeneralData.message.edit({
                embeds: [new MessageEmbed()
                    .setColor("#008B00")
                    .setAuthor({ name: "JishakuNJS" })
                    .setTitle("Module Reloaded")
                    .setDescription(`The module ${module_arg.toString()} [Type: Slash Command] was reloaded successfully.`)
                    .setTimestamp()
                    .setFooter({
                        text: `${client.user.username}`,
                        iconURL: client.user.displayAvatarURL()
                    })], ephemeral: false
            })
        }
    }
    if (interaction.options._subcommand === "shutdown") {
        await await GeneralData.message.edit({
            embeds: [new MessageEmbed()
                .setColor("#008B00")
                .setAuthor({ name: "JishakuNJS" })
                .setTitle("Shutting Down...")
                .setDescription(`The bot will shutdown in 5 seconds. There is no way to stop this process.`)
                .setTimestamp()
                .setFooter({
                    text: `${client.user.username}`,
                    iconURL: client.user.displayAvatarURL()
                })], ephemeral: true
        })
        setTimeout(() => {
            client.destroy()
        }, 5000)
    }
    if (interaction.options._subcommand === "exit-node") {
        const row = new MessageActionRow()
            .addComponents(
                new MessageButton()
                    .setCustomId('exit_jsk_shtdn')
                    .setLabel('Exit')
                    .setStyle('DANGER'),
            );
        await GeneralData.message.edit({
            embeds: [new MessageEmbed()
                .setColor("#008B00")
                .setAuthor({ name: "JishakuNJS" })
                .setTitle("Are you sure?")
                .setDescription(`Are you sure you want to exit the node process? This will shutdown the bot & kill the current process on PID ${process.pid}?\n\nPress Exit to confirm.`)
                .setTimestamp()
                .setFooter({
                    text: `${client.user.username}`,
                    iconURL: client.user.displayAvatarURL()
                })], ephemeral: true, components: [row]
        })
        const collector = GeneralData.message.createMessageComponentCollector({ componentType: 'BUTTON', time: 30000 });

        collector.on('collect', async i => {
            if (i.user.id !== GeneralData.user_id) return await i.reply({
                embeds: [new MessageEmbed()
                    .setColor("#8B0000")
                    .setAuthor({ name: "An Error Occurred" })
                    .setTitle("Unauthorized Action")
                    .setDescription(`You are not the user who ran this command. Please wait for them to respond.`)
                    .setTimestamp()
                    .setFooter({
                        text: `${client.user.username}`,
                        iconURL: client.user.displayAvatarURL()
                    })], ephemeral: true
            })
            await i.deferUpdate()
            await GeneralData.message.edit({
                embeds: [new MessageEmbed()
                    .setColor("#008B00")
                    .setAuthor({ name: "JishakuNJS" })
                    .setTitle("Running Task")
                    .setDescription(`Shutting down & Exiting Node Process...\nThis process can not be stopped.`)
                    .setTimestamp()
                    .setFooter({
                        text: `${client.user.username}`,
                        iconURL: client.user.displayAvatarURL()
                    })], ephemeral: true, components: []
            })
            setTimeout(function () {
                client.destroy()
                process.exit()
            }, 5000)
        });

        collector.on('end', async collected => {
            await GeneralData.message.edit({
                embeds: [new MessageEmbed()
                    .setColor("#8B0000")
                    .setAuthor({ name: "JishakuNJS" })
                    .setTitle("Task Canceled")
                    .setDescription(`You did not respond fast enough, the task was canceled.`)
                    .setTimestamp()
                    .setFooter({
                        text: `${client.user.username}`,
                        iconURL: client.user.displayAvatarURL()
                    })], ephemeral: false, components: []
            })
        });
    }
    if (interaction.options._subcommand === "reload-all") {
        function delay(time) {
            return new Promise(resolve => setTimeout(resolve, time));
        }
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
        await GeneralData.message.edit({
            embeds: [new MessageEmbed()
                .setColor("#FFFFFF")
                .setAuthor({ name: "JishakuNJS" })
                .setTitle("Reloading Modules")
                .setDescription(`Reloading ${Array.from(client.commands).length} Modules of type Command.`)
                .setTimestamp()
                .setFooter({
                    text: `${client.user.username}`,
                    iconURL: client.user.displayAvatarURL()
                })], ephemeral: false
        })
        async function reloadMod(k) {
            return new Promise(async (resolve, reject) => {
                requireAsync(`/home/allstar/allstar/commands/${k}.js`, function (err, module) {
                    if (err) throw err;
                    client.commands.set(k, module.exports)
                    resolve(0)
                })
            })
        }
        for (var kv of Array.from(client.commands)) {
            var pos = +Array.from(client.commands).indexOf(kv) + +1;
            var len = Array.from(client.commands).length;
            var k = kv[0],
                v = kv[1];
            var commandFile = client.commands.get(k)
            if (!commandFile) {
                await GeneralData.message.edit({
                    embeds: [new MessageEmbed()
                        .setColor("#FF0000")
                        .setAuthor({ name: "An Error Occurred" })
                        .setTitle(`Failed to reload module`)
                        .setDescription(`There was an error when reloading module ${k} [Type: Command]. There may be an error in the modules code.`)
                        .setTimestamp()
                        .setFooter({
                            text: `${client.user.username}`,
                            iconURL: client.user.displayAvatarURL()
                        })], ephemeral: false
                })
                break;
            }
            var deleted = client.commands.delete(k)
            if (!deleted) {
                await GeneralData.message.edit({
                    embeds: [new MessageEmbed()
                        .setColor("#8B0000")
                        .setAuthor({ name: "An Error Occured" })
                        .setTitle("Module Not Deleted")
                        .setDescription(`The module ${module_arg.toString().toLowerCase()} could not be deleted for an unkonwn reason.`)
                        .setTimestamp()
                        .setFooter({
                            text: `${client.user.username}`,
                            iconURL: client.user.displayAvatarURL()
                        })], ephemeral: false
                })
                break;
            }
            var module = await requireAsync(`/home/allstar/allstar/commands/${k}.js`)
            client.commands.set(k, module.exports)
        }
        await GeneralData.message.edit({
            embeds: [new MessageEmbed()
                .setColor("#FFFFFF")
                .setAuthor({ name: "JishakuNJS" })
                .setTitle("All Modules Reloaded")
                .setDescription(`Reloaded ${Array.from(client.commands).length} Modules successfully.`)
                .setTimestamp()
                .setFooter({
                    text: `${client.user.username}`,
                    iconURL: client.user.displayAvatarURL()
                })], ephemeral: false
        })
    }
}
