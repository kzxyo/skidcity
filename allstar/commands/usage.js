var os = require("os")
var osu = require("os-utils")
const si = require('systeminformation');
var memStat = require('mem-stat');
const { MessageEmbed } = require("discord.js")
const parseMilliseconds = require('parse-ms');


module.exports = {
  name: 'usage',
  description: 'Displays system usage.',
  aliases: [],
  usage: '\```usage \```',
  category: "information",
  guildOnly: false,
  args: false,
  permissions: {
    bot: [],
    user: [],
  },
  execute: async (message, args, client) => {


    try {
      var loadingEmbed = new MessageEmbed()
        .setColor("#FFFFFF")
        .setTitle("Fetching Information <a:vile_loading:1045004235915411536>")
        .setDescription("Please wait while the process is gathering information about the system.")
        .setTimestamp()
        .setFooter({
          text: `${client.user.username}`,
          iconURL: client.user.displayAvatarURL()
        });
      var msg = await message.reply({ embeds: [loadingEmbed] })
      async function cpuUsage() {
        return new Promise(function (resolve, reject) {
          osu.cpuUsage(function (v) {
            resolve(v)
          })
        })
      }
      async function cpuTemp() {
        return new Promise(function (resolve, reject) {
          si.cpuTemperature()
            .then(data => {
              resolve(data.main.toString() + " °C")
            })
        })
      }
      var cpu = await cpuUsage()
      var temp = await cpuTemp()
      var cpuModel = os.cpus()[0].model.toString()
      var uptime = function (seconds) {
        var parsed = parseMilliseconds(seconds * 1000)
        var string = ""
        if (parsed.seconds !== 0) string = `${parsed.seconds}s` + string
        if (parsed.minutes !== 0) string = `${parsed.minutes}m ` + string
        if (parsed.hours !== 0) string = `${parsed.hours}h ` + string
        if (parsed.days !== 0) string = `${parsed.days}d ` + string
        return string
      }
      var bot_uptime = uptime(process.uptime())
      var machine_uptime = uptime(os.uptime())
      var used = (memStat.total("GiB") - memStat.free("GiB")).toFixed(2)
      var total = Math.round(memStat.total("GiB"))
      var prec = memStat.usedPercent().toFixed(2);
      var embed = new MessageEmbed()
        .setColor(0xFFFFFF)
        .setTitle('Usage Info')
        .setDescription('Current usage data & stats are displayed below.')
        .addFields(
          { name: 'Status', value: `Operational`, inline: true },
          { name: 'Bot Uptime', value: `${bot_uptime}`, inline: true },
          { name: 'Machine Uptime', value: `${machine_uptime}`, inline: true },
          { name: 'Current CPU', value: `${cpuModel}`, inline: false },
          { name: 'CPU Usage', value: `${parseFloat(cpu * 100).toFixed(1)}%`, inline: true },
          { name: 'CPU Temp', value: `${temp}`, inline: true },
          { name: 'Memory Used', value: `${used}GiB / ${total}GiB [${prec}%]`, inline: true }
        )
        .setTimestamp()
        .setFooter({ text: `${client.user.username}`, iconURL: client.user.displayAvatarURL() });
      await msg.edit({ embeds: [embed] });
    } catch (e) {
      var failedEmbed = new MessageEmbed()
        .setColor("#8B0000")
        .setTitle("Process Failed <a:vile_error:1045004235915411536>")
        .setDescription("An unknown error has occurred when fetching the information this process has requested.")
        .setTimestamp()
        .setFooter({
          text: `${client.user.username}`,
          iconURL: client.user.displayAvatarURL()
        });
      message.channel.send({ embeds: [failedEmbed] })
    }


  }
};

module.exports.handler = async (client) => {
  try {
    async function cpuUsage() {
      return new Promise(function (resolve, reject) {
        osu.cpuUsage(function (v) {
          resolve(v)
        })
      })
    }
    async function cpuTemp() {
      return new Promise(function (resolve, reject) {
        si.cpuTemperature()
          .then(data => {
            resolve(data.main.toString() + " °C")
          })
      })
    }
    var cpu = await cpuUsage()
    var temp = await cpuTemp()
    var cpuModel = os.cpus()[0].model.toString()
    var uptime = function (seconds) {
      var parsed = parseMilliseconds(seconds * 1000)
      var string = ""
      if (parsed.seconds !== 0) string = `${parsed.seconds}s` + string
      if (parsed.minutes !== 0) string = `${parsed.minutes}m ` + string
      if (parsed.hours !== 0) string = `${parsed.hours}h ` + string
      if (parsed.days !== 0) string = `${parsed.days}d ` + string
      return string
    }
    var bot_uptime = uptime(process.uptime())
    var machine_uptime = uptime(os.uptime())
    var used = (memStat.total("GiB") - memStat.free("GiB")).toFixed(2)
    var total = Math.round(memStat.total("GiB"))
    var prec = memStat.usedPercent().toFixed(2);
    var embed = new MessageEmbed()
      .setColor(0xFFFFFF)
      .setTitle('Usage Info')
      .setDescription('Current usage data & stats are displayed below.')
      .addFields(
        { name: 'Status', value: `Operational`, inline: true },
        { name: 'Bot Uptime', value: `${bot_uptime}`, inline: true },
        { name: 'Machine Uptime', value: `${machine_uptime}`, inline: true },
        { name: 'Current CPU', value: `${cpuModel}`, inline: false },
        { name: 'CPU Usage', value: `${parseFloat(cpu * 100).toFixed(1)}%`, inline: true },
        { name: 'CPU Temp', value: `${temp}`, inline: true },
        { name: 'Memory Used', value: `${used}GiB / ${total}GiB [${prec}%]`, inline: true },
        { name: 'Message Updated:', value: `<t:${Math.floor(Date.now() / 1000)}:F>`, inline: false }
      )
      .setTimestamp()
      .setFooter({ text: `${client.user.username}`, iconURL: client.user.displayAvatarURL() });
    return {
      status: 0,
      embed: embed
    }
  } catch (e) {
    return {
      status: 1
    }
  }
}