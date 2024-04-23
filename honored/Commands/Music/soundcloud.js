const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'soundcloud',
        description: 'Search for a song on SoundCloud',
        syntax: 'soundcloud [query]',
        example: 'soundcloud patchmade',
        parameters: 'query',
        aliases: ['sc'],
        permissions: 'N/A',
        module: 'music'
    },
    run: async (session, message, args, prefix) => {
        try {
            if (!args[0]) {
                return displayCommandInfo(module.exports, session, message);
            }

            const results = await axios.get(`https://api-v2.soundcloud.com/search/tracks?q=${args.join(' ')}`, {
                headers: {
                    'Authorization': `OAuth 2-292593-994587358-Af8VbLnc6zIplJ`
                }
            }).then(response => response.data)
              .catch(error => {
                  console.error('Error:', error.message);
                  return message.channel.send({
                      embeds: [
                          new MessageEmbed()
                              .setColor(session.warn)
                              .setDescription(`${session.mark} ${message.author}: The **API** returned a bad response`)
                      ]
                  });
              });

            if (!results.collection.length) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.warn)
                            .setDescription(`${session.mark} ${message.author}: No results found for **${args.join(' ')}**`)
                    ]
                });
            }

            message.channel.send(`${results.collection[0].permalink_url}`);

            if (!args[0]) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.color)
                            .setTitle('Command: soundcloud')
                            .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                            .setDescription('Search SoundCloud for a track\n```Syntax: soundcloud [query]\nExample: soundcloud KNOW DAT```')
                    ]
                });
            }
        } catch (error) {
            console.error('Error while executing soundcloud command:', error);
            const errorEmbed = new MessageEmbed()
            .setColor(session.warn)
            .setDescription(`${session.mark} ${message.author}: API returned an errorr`);
            return message.channel.send({ embeds: [errorEmbed] });
        }
    }
};
