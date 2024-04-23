const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const pagination = require('/root/rewrite/Utils/paginator.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'animesearch',
        aliases: ['anime'],
        description: 'Search an Anime on Kitsu.io',
        syntax: 'anime <title>',
        example: 'anime Naruto Shippuden'
    },
    run: async (session, message, args) => {
        if (args.length === 0) {
            return displayCommandInfo(module.exports, session, message);
        }

        const title = args[0];

        try {
            const response = await axios.get(`https://kitsu.io/api/edge/anime?filter[text]=${encodeURIComponent(title)}`);
            const data = response.data.data;

            if (!data || !data.length) return message.channel.send({ embeds: [
                new MessageEmbed()
                .setDescription(`${session.mark} ${message.author}: No results found for **${title}**`)
                .setColor(session.warn)
            ]});

            const embeds = data.map(anime => {
                return new MessageEmbed()
                    .setColor(session.color)
                    .setTitle(anime.attributes.titles.en ? `${anime.attributes.titles.en} (Japanese: ${anime.attributes.titles.en_jp})` : anime.attributes.titles.en_jp)
                    .setDescription(anime.attributes.synopsis)
                    .addFields({
                        name: 'Age Rating',
                        value: `${anime.attributes.ageRating}${anime.attributes.ageRatingGuide ? ` (${anime.attributes.ageRatingGuide})` : ''}`,
                        inline: true
                    })
                    .addFields({
                        name: 'Episodes',
                        value: `${anime.attributes.episodeCount} (${anime.attributes.episodeLength} Min Per Episode)`,
                        inline: true
                    })
                    .addFields({
                        name: 'Date Aired',
                        value: `**Start:** ${anime.attributes.startDate}\n**End:** ${anime.attributes.endDate}`
                    })
                    .setImage(anime.attributes.coverImage && anime.attributes.coverImage.original)
                    .setThumbnail(anime.attributes.posterImage && anime.attributes.posterImage.original)
                    .setURL(`https://kitsu.io/anime/${anime.id}`);
            });

            pagination(session, message, embeds, embeds.length, data.length, `Search Results for ${title}`, ':tv:');
            
        } catch (error) {
            console.error('Error fetching anime data:', error);
            return message.reply('An error occurred while fetching anime data.');
        }
    }
};
