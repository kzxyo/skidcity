const { MessageEmbed, Permissions } = require("discord.js");
const { prefix, embedcolor } = require('./../../config.json')
const globaldataschema = require('../../database/global')

module.exports = {
  name: "copyembed",
  aliases: ['copy'],
  description: 'copy an embed json code',
  usage: '{guildprefix}copyembed [message id]',
  run: async(client, message, args) => {

    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    if(!message.member.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires \`manage messages\` permission`)

    if(!message.guild.me.permissions.has(Permissions.FLAGS.MANAGE_MESSAGES)) return message.channel.send(`this command requires me to have \`manage messages\` permission`)

    try {

      if (!args[0]) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}copyembed`)
        .setDescription('copy an embed json code')
        .addFields(
        { name: '**usage**', value: `${guildprefix}copyembed [message id]`, inline: false },
        { name: '**aliases**', value: 'copy', inline: false },
        )
        return message.channel.send({ embeds: [embed] })   
      }

      const copyembed = await message.channel.messages.fetch(args[0])

      if (!copyembed) {

        const embed = new MessageEmbed()

        .setColor(embedcolor)
        .setTitle(`${guildprefix}copyembed`)
        .setDescription('copy an embed json code')
        .addFields(
        { name: '**usage**', value: `${guildprefix}copyembed [message id]`, inline: false },
        { name: '**aliases**', value: 'copy', inline: false },
        )
        return message.channel.send({ embeds: [embed] })
      }

      const json = toJSON(copyembed.content, copyembed.embeds[0])

      const copiedembed = new MessageEmbed()

      .setColor(embedcolor)
      .setDescription(`the current embed message:\n\`\`\`json\n${json}\`\`\``)
      .setFooter({ text: `successfully copied the embed code` })

      return message.channel.send({ embeds: [copiedembed] })

    } catch (error) {

      if (error.code === 404) {
        return message.channel.send('an error occured')
      }
    }

    function toJSON(content, messageEmbed) {
	    let json = {};
	    if (content)
		  json.content = content;
	    json.embed = {};
	    if (messageEmbed.title)
		  json.embed.title = messageEmbed.title;
	    if (messageEmbed.description)
		  json.embed.description = messageEmbed.description;
 	    if (messageEmbed.url)
		  json.embed.url = messageEmbed.url;
	    if (messageEmbed.color)
		  json.embed.color = messageEmbed.color;
	    if (messageEmbed.timestamp)
		  json.embed.timestamp = new Date(messageEmbed.timestamp);
	    if (messageEmbed.footer) {
		  json.embed.footer = {};
		  if (messageEmbed.footer.iconURL)
		  json.embed.footer.icon_url = messageEmbed.footer.iconURL;
		  if (messageEmbed.footer.text)
		  json.embed.footer.text = messageEmbed.footer.text;
	  }
	  if (messageEmbed.thumbnail) {
		  json.embed.thumbnail = {};
		  if (messageEmbed.thumbnail.url)
		  json.embed.thumbnail.url = messageEmbed.thumbnail.url;
	  }
	  if (messageEmbed.image) {
		  json.embed.image = {};
		  if (messageEmbed.image.url)
		  json.embed.image.url = messageEmbed.image.url;
	  }
	  if (messageEmbed.author) {
		  json.embed.author = {};
		  if (messageEmbed.author.url)
		  json.embed.author.url = messageEmbed.author.url;
		  if (messageEmbed.author.name)
		  json.embed.author.name = messageEmbed.author.name;
		  if (messageEmbed.author.iconURL)
		  json.embed.author.icon_url = messageEmbed.author.iconURL;
	  }
	    if (messageEmbed.fields)
	    json.embed.fields = messageEmbed.fields;
	    return JSON.stringify(json, undefined, 2);
    }
  }
}