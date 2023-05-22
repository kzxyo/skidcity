const { EmbedBuilder } = require('discord.js')

module.exports = class Error {
    constructor (Message, Command, Error) {
        console.log(Error)
        
        function CreateID (AllowedCharacters) { 
            var Text = ''

            for (var i = 0; i < 24; i++) Text += AllowedCharacters.charAt(Math.floor(Math.random() * AllowedCharacters.length))

            return Text
        }

        const ErrorID = CreateID('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        Message.channel.send({
            embeds : [
                new EmbedBuilder({
                    description : `An error occured while **${Command}** was being executed. Try again later.`,
                    footer : {
                        text : `Join our Support Server (blair.win/discord) and report "${ErrorID}"`
                    }
                }).setColor(Message.client.Color)
            ]
        }).then(async (ErrorMessage) => {
            Message.client.Database.query(`INSERT INTO tracebacks (guild_id, channel_id, user_id, message_id, error_id, error, timestamp, command) VALUES (${Message.guild.id}, ${Message.channel.id}, ${Message.author.id}, ${ErrorMessage.id}, '${ErrorID}', '${Error.message}', '${Message.createdTimestamp}', '${Command}')`)
        })
    }
}