const { MessageEmbed } = require("discord.js");
const imdb = require("imdb-api");
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: "movie",
        aliases: ["series", "show"],
        description: "Get the information about a movie or series.",
        category: "info",
        syntax: "movie [query]",
        example: "movie Guy",
        permissions: "N/A",
        parameters: "movie",
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        if (!args.length) {
            return displayCommandInfo(module.exports, session, message);
        }

        const imdbClient = new imdb.Client({ apiKey: "5e36f0db" });
        try {
            const movie = await imdbClient.get({ name: args.join(" ") });

            const embed = new MessageEmbed()
                .setTitle(movie.title)
                .setColor(session.color)
                .setThumbnail(movie.poster)
                .setDescription(movie.plot)
                .setFooter(`Ratings: ${movie.rating}`)
                .addField("Country", movie.country, true)
                .addField("Languages", movie.languages, true)
                .addField("Type", movie.type, true);

            message.channel.send({ embeds: [embed] });
        } catch (error) {
            console.error("Error fetching IMDb information:", error);
            message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: No results found for **${args.join(" ")}**`)
            ]});
        }
    }
};
