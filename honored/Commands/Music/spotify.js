const { MessageEmbed } = require('discord.js')
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
const SpotifyWebApi = require('spotify-web-api-node');
const SpotifyClient = new SpotifyWebApi({
    clientId: '',
    clientSecret: ''
});

module.exports = {
    configuration: {
        commandName: 'spotify',
        aliases: ['sp'],
        description: 'Search spotify for a song',
        syntax: 'spotify [query]',
        example: 'spotify patchmade',
        permissions: 'N/A',
        parameters: 'song',
        module: 'music'
    },

    run: async (session, message, args) => {
        try {
            const query = args.join(' ');

            if (!query) {
                return displayCommandInfo(module.exports, session, message);
            }

            const credentials = await SpotifyClient.clientCredentialsGrant();
            SpotifyClient.setAccessToken(credentials.body['access_token']);

            const { body: { tracks } } = await SpotifyClient.searchTracks(query);

            if (!tracks || tracks.items.length === 0) {
                return message.channel.send({ embeds: [
                    new MessageEmbed()
                        .setColor(session.warn)
                        .setDescription(`${session.mark} ${message.author}: No results found for **${query}**`)
                ]});
            }

            const track = tracks.items[0];

            message.channel.send(track.external_urls.spotify);
        } catch (error) {
            session.log('Error:', error.message);
            const errorEmbed = new MessageEmbed()
            .setColor(session.warn)
            .setDescription(`${session.mark} ${message.author}: API returned an errorr`);
            return message.channel.send({ embeds: [errorEmbed] });
        }
    }
};
