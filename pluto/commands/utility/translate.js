const Discord = require('discord.js')
const { color } = require('./../../config.json')
const translate = require('translate-google')
const globaldataschema = require('../../database/global')

module.exports= {
    name : 'translate',
  aliases: ["translator"],
    run : async(client, message, args) => {

        const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
        if (globaldata) {
          var guildprefix = globaldata.Prefix
        } else if (!globaldata) {
          guildprefix = prefix
        }

        translate(args.join(" "), {to : 'en'}).then(res => {
            message.channel.send(res)
        }).catch(err => {
            const embed = new Discord.MessageEmbed()
            .setColor(color)
            .setTitle(`${guildprefix}translate`)
            .setDescription('translate a message')
            .addFields(
            { name: '**usage**', value: `${guildprefix}translate [word]\n${guildprefix}translate picka`, inline: false },
            { name: '**aliases**', value: `translator`, inline: false },
            )
  if (!args[0]) return message.channel.send({embeds: [embed]})
            console.log(err)
        })
    }
}