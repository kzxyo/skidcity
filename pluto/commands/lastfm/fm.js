const { MessageEmbed } = require("discord.js");
const { prefix, embedcolor, lastfmapikey } = require('./../../config.json')
const globaldataschema = require('../../database/global')
const lastfmuserschema = require('../../database/lastfm')
const request = require("superagent");
var rp = require('request-promise');
var commaNumber = require('comma-number')

module.exports = {
  name: "fm",
  aliases: ['np'],
  description: 'gets latest activity from last.fm',
  subcommands: '',
  usage: '{guildprefix}fm',
  run: async(client, message, args) => {
  
    const globaldata = await globaldataschema.findOne({ GuildID: message.guild.id })
  
    if (globaldata) {
      var guildprefix = globaldata.Prefix
    } else if (!globaldata) {
      guildprefix = prefix
    }

    const fmdata = await lastfmuserschema.findOne({ UserID: message.author.id })

    if (!fmdata) {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setDescription(`you don't have a last.fm linked, use \`${guildprefix}lastfm set [username]\``)

      return message.channel.send({ embeds: [embed] })
    }

    let fmuser = fmdata.Username

    var options = {
      uri: "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" + fmuser + "&api_key= " + lastfmapikey + "&format=json&extended=1",
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
      var trackURL = "http://ws.audioscrobbler.com/2.0/?method=track.getInfo&username=" + fmuser + "&api_key=43693facbb24d1ac893a7d33846b15cc&artist=" + artistName + "&track=" + trackName + "&format=json&autocorrect=1";
      var options2 = {
        uri: trackURL,
        headers: {
          'Connection': 'keep-alive',
          'Accept-Encoding': '',
          'Accept-Language': 'en-US,en;q=0.8',
        },
        json: true
      };
      rp(options2)
      .then(function (track) {
        try {
          var playCount = '?';
          if (track.track.userplaycount != undefined) {
            playCount = track.track.userplaycount;
          }
        } catch (error) {
          playCount = '0';
        }

        let artist = "";
        let trackName = "";
        let cover = "";
        let album = "";
        const result = request.get(`http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user=${fmuser}&api_key=43693facbb24d1ac893a7d33846b15cc&format=json&limit=1`)
        
        result.then(res => {

          const track = res.body.recenttracks.track[0];
          artist = track.artist["#text"];
          trackName = track.name;
          album = track.album["#text"];
          total = track.total;
          cover = track.image[0]["#text"];
          var trackName2 = lastfm.recenttracks.track[0].name.replace(/ /g, "+");
          var artistName = lastfm.recenttracks.track[0].artist.name.replace(/ /g, '+');
          artistURL2 = "https://www.last.fm/music/" + artistName;
          var spacer = "/_/"
          let url = "https://www.last.fm/user/" + fmuser;
          let trackURL1 = "https://www.last.fm/music/" + artistName + album;
          let trackURL2 = "https://www.last.fm/music/" + artistName + spacer + trackName2;
          let format = commaNumber.bindWith(',', '.')
          let result = format(playCount)
          let result2 = format(lastfm.recenttracks['@attr'].total)

          try {

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setAuthor({ name: `${fmuser} — Now Playing`, iconURL: '', url: `${url}` })
            //.setTitle(`${fmuser} — Now Playing`)
            //.setURL(url)
            .setDescription(`[**${trackName}**](${trackURL2})\nalbum: **${album}**\nartist: [**${artist}**](${artistURL2})`)
            .setThumbnail(track.image[3]["#text"])
            .setFooter({ text: `${result + " plays — " + result2 + " scrobbles total"}` })
            .setTimestamp()
          
            return message.channel.send({ embeds: [embed] }).then(embedMessage => {
              embedMessage.react("🔥").then(embedMessage.react("🗑️"))
            });

          } catch (error) {

            const embed = new MessageEmbed()

            .setColor(embedcolor)
            .setDescription(`\`service unavailable\` - the last.fm service may be having issues, please try again later. this is usually not a bot-related issue — for any updates, check [@lastfmstatus](https://twitter.com/lastfmstatus) on Twitter`)
            .setThumbnail('https://www.last.fm/static/images/marvin.png')

            return message.channel.send({ embeds: [embed] })
          }
        })
      })
    }).catch(() => {

      const embed = new MessageEmbed()

      .setColor(embedcolor)
      .setDescription(`this last.fm account doesn't exist, use \`${guildprefix}lastfm set\` to change it`)

      return message.channel.send({ embeds: [embed] })
    })
  }
}