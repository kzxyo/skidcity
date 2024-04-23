const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'birthday',
        aliases: ['bday'],
        description: 'See how far your birthday is',
        syntax: 'birthday [month] (day)',
        example: 'birthday december 24th',
        permissions: 'N/A',
        parameters: 'month, day',
        module: 'utility'
    },
    run: async (session, message, args) => {
        if (args.length !== 2) {
            return displayCommandInfo(module.exports, session, message);
        }
        const providedMonth = args[0].toLowerCase();
        const providedDay = parseInt(args[1]);
        const months = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ];
        const monthIndex = months.indexOf(providedMonth);
        if (monthIndex === -1) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: Please provide a valid month`)
                ]
            });
        }
        if (isNaN(providedDay) || providedDay < 1 || providedDay > 31) {
            return message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: Please provide a valid day`)
                ]
            });
        }
        const currentDate = new Date();
        const currentYear = currentDate.getFullYear();
        const birthdayDate = new Date(currentYear, monthIndex, providedDay);
        let difference = birthdayDate - currentDate;
        if (difference < 0) {
            birthdayDate.setFullYear(currentYear + 1);
            difference = birthdayDate - currentDate;
        }
        const daysUntilBirthday = Math.ceil(difference / (1000 * 60 * 60 * 24));

        return message.channel.send({
            embeds: [
                new MessageEmbed()
                    .setColor(session.color)
                    .setDescription(`:birthday: ${message.author}: Your birthday is in **${daysUntilBirthday}** days`)
            ]
        });
    }
};
