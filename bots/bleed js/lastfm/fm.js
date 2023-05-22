const { MessageEmbed } = require("discord.js");
const request = require("superagent");
const low = require('lowdb')
var rp = require('request-promise');
var commaNumber = require('comma-number')
let db2 = require('quick.db')
const { default_prefix } = require("../../config.json");
const { color } = require("../../config.json");
const { lastfm } = require("../../emojis.json");

module.exports = {
    name: "fm",
    aliases: ["lfm", "np"],
    usage: "fm",
    category: "lastfm",

    run: (client, message, args) => {
        let member = message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.member;

        let prefix2 = db2.get(`prefix_${message.guild.id}`)
        const args1 = message.content.trim().split(/ +/g)
        if (prefix2 === null) { prefix2 = default_prefix; }
        const FileSync = require('lowdb/adapters/FileSync')
        const adapter = new FileSync('fmuser.json');
        const db = low(adapter);
        const user = message.author
        let [fmUser] = args;
        if (!fmUser) {
            const dbUser = db
                .get('users')
                .find({
                    userID: message.author.id
                })
                .value();
            if (message.author.bot) return;
            if (!dbUser) {
                message.channel.send({
                    embed: {
                        color: "#d1202a", description: `${lastfm} ${message.author}: Looks like you dont have your username set.
You can connect your **Last.fm** using \`${prefix2}lastfm set <username>\``
                    }
                })
            }
            fmUser = dbUser.lastFM;
        }
        var options = {
            uri: "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" + fmUser + "&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&extended=1",
            headers: {
                'Connection': 'keep-alive',
                'Accept-Encoding': '',
                'Accept-Language': 'en-US,en;q=0.8',
            },
            json: true
        }
        rp(options)
            .then(function (lastfm) {
                var trackName = lastfm.recenttracks.track[0].name.replace(/ /g, "+");
                var artistName = lastfm.recenttracks.track[0].artist.name.replace(' ', '+');
                var trackURL = "http://ws.audioscrobbler.com/2.0/?method=track.getInfo&username=" + fmUser + "&api_key=43693facbb24d1ac893a7d33846b15cc&artist=" + artistName + "&track=" + trackName + "&format=json&autocorrect=1";
                var options2 = {
                    uri: trackURL,
                    headers: {
                        'Connection': 'keep-alive',
                        'Accept-Encoding': '',
                        'Accept-Language': 'en-US,en;q=0.8',
                    },
                    json: true
                };
                message.channel.startTyping();
                rp(options2)
                    .then(function (track) {
                        try {
                            var playCount = '?';
                            if (track.track.userplaycount != undefined) {
                                playCount = track.track.userplaycount;
                            }
                        } catch (error) {
                            playCount = '?';
                        }

                        let artist = "";
                        let trackName = "";
                        let cover = "";
                        let album = "";
                        const result = request.get(`http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user=${fmUser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=1`)
                        result.then(res => {
                            const track = res.body.recenttracks.track[0];
                            artist = track.artist["#text"];
                            artistURL2 = "https://www.last.fm/music/" + artistName;
                            trackName = track.name;
                            album = track.album["#text"];
                            total = track.total;
                            cover = track.image[0]["#text"];
                            var trackName2 = lastfm.recenttracks.track[0].name.replace(/ /g, "+");
                            var artistName = lastfm.recenttracks.track[0].artist.name.replace(/ /g, '+');
                            var spacer = "/_/"
                            let url = "https://www.last.fm/user/" + fmUser;
                            let trackURL2 = "https://www.last.fm/music/" + artistName + spacer + trackName2;
                            let format = commaNumber.bindWith(',', '.')
                            let result = format(playCount)
                            let result2 = format(lastfm.recenttracks['@attr'].total)

                            try {
                                const embed = new MessageEmbed()
                                    .setAuthor(`Last.fm: ${fmUser}`, message.author.displayAvatarURL({ dynamic: true }), `${url}`)
                                    .setColor(member.displayHexColor || color)
                                    .setThumbnail(track.image[3]["#text"])
                                    .setDescription(`[**${trackName}**](${trackURL2})\nBy [**${artist}**](${artistURL2})・**${album}**`)
                                    .setFooter("Plays: " + result + "・Total Scrobbles: " + result2 + ``)
                                    .setTimestamp()
                                message.channel.stopTyping(true);
                                message.channel.send(embed).then(embedMessage => {
                                    embedMessage.react("👍").then(embedMessage.react("👎"))
                                });
                            } catch (error) {
                                console.log(error)
                                message.channel.send({ embed: { color: "#d1202a", description: `${lastfm} **Last.fm**: Operation failed - The backend service most likely failed, please try again` } })
                            }
                        })
                    }
                    )
            })
    }
}