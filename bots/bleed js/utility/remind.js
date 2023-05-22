const Discord = require('discord.js');
const { color } = require("../../config.json");
const { warn } = require('../../emojis.json')

module.exports = {
	name: "remind",
	aliases: ["reminder", "rm"],
	category: "utility",

	run: async (client, message, args) => {
		const remindEmbed = new Discord.MessageEmbed()
			.setAuthor(message.author.username, message.author.avatarURL({
				dynamic: true
			}))
			.setTitle('Command: remind')
			.setDescription('Get reminders for a duration set about whatever you choose')
			.addField('**Aliases**', 'reminder, rm', true)
			.addField('**Parameters**', 'time, text', true)
			.addField('**Information**', `N/A`, true)
			.addField('**Usage**', '\`\`\`Syntax: remind (duration) <reason>\nExample: remind 1h To get food\`\`\`')
			.setFooter(`Module: moderation`)
			.setTimestamp()
			.setColor(color)
		if (!args[0]) return message.channel.send(remindEmbed)

		var time = args[0];
		var reminder = args.splice(1).join(' ');

		if (!time) return message.channel.send('so you want me to remind you nothing?');
		if (!reminder) return message.channel.send('so you want me to remind you nothing?');

		// This will not work if the bot is restarted or stopped

		time = await time.toString();

		if (time.indexOf('s') !== -1) { // Seconds
			var timesec = await time.replace(/s.*/, '');
			var timems = await timesec * 1000;
		} else if (time.indexOf('m') !== -1) { // Minutes
			var timemin = await time.replace(/m.*/, '');
			timems = await timemin * 60 * 1000;
		} else if (time.indexOf('h') !== -1) { // Hours
			var timehour = await time.replace(/h.*/, '');
			timems = await timehour * 60 * 60 * 1000;
		} else if (time.indexOf('d') !== -1) { // Days
			var timeday = await time.replace(/d.*/, '');
			timems = await timeday * 60 * 60 * 24 * 1000;
		} else {
			return message.channel.send({ embed: { color: "#efa23a", description: `${warn} ${message.author}: The time must be in the format of **<number>[s/m/h/d]**` } });
		}

		message.channel.send(`ok ill remind u in ${time}`);

		setTimeout(function () {
			message.author.send({ embed: { color: "#6495ED", text: `${message.author}`, description: `:alarm_clock: You wanted me to remind you to: **${reminder}** (\`${time}\`)` } });
		}, parseInt(timems));

	}
}