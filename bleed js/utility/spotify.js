const Discord = require('discord.js');
const convert = require('parse-ms');

module.exports = {
    name: "spotify",
    aliases: ["sp"],
    category: "utility",

run: async (client, message, args) => {
    let user;
    if (message.mentions.users.first()) {
        user = message.mentions.users.first();
    } else {
        user = message.author;
    }

    let status;
    if (user.presence.activities.length === 1) status = user.presence.activities[0];
    else if (user.presence.activities.length > 1) status = user.presence.activities[1];

    if (user.presence.activities.length === 0 || status.name !== "Spotify" && status.type !== "LISTENING") {
      const spotifyEmbed = new Discord.MessageEmbed()
      .setColor("#efa23a")
      .setDescription(`<:warn:823958404455989288> ${message.author}: User isn't playing anything on spotify`)
        return message.channel.send(spotifyEmbed);
    }

    if (status !== null && status.type === "LISTENING" && status.name === "Spotify" && status.assets !== null) {
        let image = `https://i.scdn.co/image/${status.assets.largeImage.slice(8)}`,
            url = `https://open.spotify.com/track${status.syncID}`,
            name = status.details,
            artist = status.state,
            album = status.assets.largeText,
            timeStart = status.timestamps.start,
            timeEnd = status.timestamps.end,
            timeConvert = convert(timeEnd - timeStart);

        let minutes = timeConvert.minutes < 10 ? `0${timeConvert.minutes}` : timeConvert.minutes;
        let seconds = timeConvert.seconds < 10 ? `0${timeConvert.seconds}` : timeConvert.seconds;
        let time = `${minutes}:${seconds}`;

        const embed = new Discord.MessageEmbed()
        .setAuthor("Spotify", "https://www.freepnglogos.com/uploads/spotify-logo-png/file-spotify-logo-png-4.png")
        .setTitle(`**${name}**`)
        .setColor("GREEN")
        .setFooter(message.author.username, message.author.avatarURL({
            dynamic: true
          }))
        .setTimestamp()
        .setThumbnail(image)
        .addField("**Album**", album, true)
        .addField("**Artist**", artist, true)
        .addField("**Duration**", time, true)
        .addField("**Listen Now On Spotify**", `[${artist} - ${name}](${url})`, true)

        return message.channel.send(embed)
    }
}
}