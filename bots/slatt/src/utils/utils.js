const { MessageEmbed } = require('discord.js');
const moment = require('moment');
const db = require('quick.db')

function time(str) {
  const input = str.match(/[1-9]/g)
  if (input) {
    const int = parseInt(input.join(''))
    let string = str.match(/[a-z]/g)
    if (string) {
      string = string.join('')
      console.log(int+string)
    } else return undefined
  } else return undefined
}

function capitalize(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}
function removeElement(arr, value) {
  var index = arr.indexOf(value);
  if (index > -1) {
    arr.splice(index, 1);
  }
  return arr;
}
function trimArray(arr, maxLen = 10) {
  if (arr.length && arr.length > maxLen) {
    const len = arr.length - maxLen;
    arr = arr.slice(0, maxLen);
    arr.push(`and **${len}** more...`);
  }
  return arr;
}
function trimStringFromArray(arr, maxLen = 2048, joinChar = '\n') {
  let string = arr.join(joinChar);
  const diff = maxLen - 15; // Leave room for "And ___ more..."
  if (string.length > maxLen) {
    string = string.slice(0, string.length - (string.length - diff));
    string = string.slice(0, string.lastIndexOf(joinChar));
    string = string + `\nAnd **${arr.length - string.split('\n').length}** more...`;
  }
  return string;
}

function getRange(arr, current, interval) {
  const max = (arr.length > current + interval) ? current + interval : arr.length;
  current = current + 1;
  const range = (arr.length == 1 || arr.length == current || interval == 1) ? `[${current}]` : `[${current} - ${max}]`;
  return range;
}

function replace_fm_variables(message, track, artist, album, np, profile_image, artist_plays, track_plays, user, track_image, total) {
  if (!message) return message;
  else return message
    .replace(/`?\{track.url}`?/g, `[${track.name}](${track.url})`)
    .replace(/`?\{artist.url}`?/g, `[${artist}](https://last.fm/music/${artist.replace(/`?\ `?/g, `+`)})`)
    .replace(/`?\{album.url}`?/g, `[${album}](https://last.fm/music/${album.replace(/`?\ `?/g, `+`)})`)
    .replace(/`?\{track}`?/g, track.name.length > 30 ? track.name.slice(0, 30) + '...' : track.name)
    .replace(/`?\{artist}`?/g, artist)
    .replace(/`?\{is.np}`?/g, np)
    .replace(/`?\{profile.image}`?/g, profile_image)
    .replace(/`?\{album}`?/g, album)
    .replace(/`?\{artist.plays}`?/g, artist_plays)
    .replace(/`?\{total.scrobbles}`?/g, total)
    .replace(/`?\{track.plays}`?/g, track_plays)
    .replace(/`?\{profile.url}`?/g, `https://last.fm/user/${user.username}`)
    .replace(/`?\{lastfm.username}`?/g, user.username)
    .replace(/`?\{track.image}`?/g, track_image)
}

function replace_all_variables(content, message, member) {
  if (!content) return content;
  else return content
    .replace(/`?\{guild.name}`?/g, message.guild.name)
    .replace(/`?\{guild.id}`?/g, message.guild.id)
    .replace(/`?\{guild.icon}`?/g, message.guild.iconURL({ dynamic: true }))
    .replace(/`?\{guild.owner_tag}`?/g, message.guild.members.cache.get(message.guild.ownerId).user.tag)
    .replace(/`?\{guild.owner_id}`?/g, message.guild.ownerId)
    .replace(/`?\{guild.owner_username}`?/g, message.guild.members.cache.get(message.guild.ownerId).user.username)
    .replace(/`?\{guild.owner_mention}`?/g, message.guild.members.cache.get(message.guild.ownerId))
    .replace(/`?\{guild.banner}`?/g, message.guild.bannerURL())
    .replace(/`?\{guild.member_count}`?/g, message.guild.memberCount)
    .replace(/`?\{guild.boost_count}`?/g, message.guild.premiumSubscriptionCount)
    .replace(/`?\{guild.role_count}`?/g, message.guild.roles.cache.size)
    .replace(/`?\{guild.channel_count}`?/g, message.guild.channels.cache.size)
    .replace(/`?\{guild.emoji_count}`?/g, message.guild.name)
    .replace(/`?\{user.avatar}`?/g, member.user.displayAvatarURL({ dynamic: true }))
    .replace(/`?\{user.username}`?/g, member.user.username)
    .replace(/`?\{user.tag}`?/g, member.user.tag)
    .replace(/`?\{user.mention}`?/g, member)
    .replace(/`?\{user.id}`?/g, member.id)
    .replace(/`?\{user.nickname}`?/g, member.nickname || '(no nickname)')
    .replace(/`?\{user.created_at}`?/g, moment(member.user.createdAt).format('MMM DD YYYY'))
    .replace(/`?\{user.joined_at}`?/g, moment(member.joinedAt).format('MMM DD YYYY'))
}

function getOrdinalNumeral(number) {
  number = number.toString();
  if (number === '11' || number === '12' || number === '13') return number + 'th';
  if (number.endsWith(1)) return number + 'st';
  else if (number.endsWith(2)) return number + 'nd';
  else if (number.endsWith(3)) return number + 'rd';
  else return number + 'th';
}
async function getCaseNumber(client, guild, modLog) {

  const message = (await modLog.messages.fetch({ limit: 100 })).filter(m => m.member === guild.me &&
    m.embeds[0] &&
    m.embeds[0].type == 'rich' &&
    m.embeds[0].footer &&
    m.embeds[0].footer.text &&
    m.embeds[0].footer.text.startsWith('Case')
  ).first();

  if (message) {
    const footer = message.embeds[0].footer.text;
    const num = parseInt(footer.split('#').pop());
    if (!isNaN(num)) return num + 1;
  }

  return 1;
}
function getStatus(...args) {
  for (const arg of args) {
    if (!arg) return 'disabled';
  }
  return 'enabled';
}


function replaceKeywords(message) {
  if (!message) return message;
  else return message
    .replace(/\{member}/g, '`member`')
    .replace(/\{username}/g, '`username`')
    .replace(/\{tag}/g, '`tag`')
    .replace(/\{size}/g, '`size`')
    .replace(/\{guild}/g, '`guild`');
}

async function send_punishment({ message, member, action, reason, info }) {
  const { stripIndent } = require('common-tags');
  const embed = new MessageEmbed()
    .setTitle(`**${action}**`)
    .setAuthor(message.author.tag, message.author.avatarURL({ dynamic: true }))
    .setColor('#303135')
    .setDescription(stripIndent`
    > **reason:** ${reason}
    > **server:** ${message.guild.name}
    ${info ? `> **info:** ${info}` : ''}
    `)
    .setThumbnail(message.guild.iconURL({ dynamic: true }))
    .setFooter(`Action taken on ${moment(Date.now()).format('YY/MM/DD')}`)
  if (member) member.send({ embeds: [embed] }).catch((e) => null)
}

async function send_log_message(message, member, module, msg) {
  const embed = new MessageEmbed()
    .setTitle(`Command: ${module}`)
    .setAuthor(member.user.tag, member.user.displayAvatarURL())
    .setColor('#303135')
    .setDescription(`> ${replace_all_variables(msg, message, member)}`)
    .addField(`Author`, `${message.author ? message.author.tag : member.user.tag}`, true)
    .addField(`Channel`, `${message.channel ? message.channel : 'No channel'}`, true)
    .addField(`Message`, `${message.url ? `[jump to message](${message.url})` : 'No Message'}`, true)
    .setFooter(`Slatt-logs`, message.client.user.displayAvatarURL())
    .setTimestamp()
  const id = db.get(`slatt_log_${message.guild.id}`)
  const channel = message.guild.channels.cache.get(id)
  if (channel) channel.send({ embeds: [embed] })
}

function rotate(json) {
  return json[Math.round(Math.random() * (json.length - 1))]
}
function convert_embed_to_string(params) {
  let arr = []
  if (params.title) arr.push(`$title ${params.title}`)
  if (params.description) arr.push(`$description ${params.description}`)
  if (params.url) arr.push(`$url ${params.url}`)
  if (params.color) arr.push(`$color ${params.color}`)
  if (params.timestamp) arr.push(`$timestamp now`)
  if (params.fields.length) {
    params.fields.forEach(field => {
      arr.push(`$field ${field.name}\n${field.value}${field.inline ? `\ntrue` : ''}`)
    })
  }
  if (params.thumbnail) arr.push(`$thumbnail ${params.thumbnail.url}`)
  if (params.image) arr.push(`$image ${params.image.url}`)
  if (params.author) {
    if (params.author.iconURL) {
      arr.push(`$author ${params.author.name} $and ${params.author.iconURL}`)
    } else {
      arr.push(`$author ${params.author.name}`)
    }
  }
  if (params.footer) {
    if (params.footer.iconURL) {
      arr.push(`$footer ${params.footer.text} $and ${params.footer.iconURL}`)
    } else {
      arr.push(`$footer ${params.footer.text}`)
    }
  }
  return arr
}
async function extract_color(img) {
  try {
    const getColors = require('get-image-colors')
    const rgb2hex = require('rgb2hex');
    const imageColor = await getColors(img)
    let rgb = `${imageColor[0]._rgb[0]}, ${imageColor[0]._rgb[1]}, ${imageColor[0]._rgb[2]}`
    let color = rgb2hex(`rgb(${rgb})`)
    return color.hex
  } catch (error) {
    return '#00000'
  }
}

function flag(content, flag) {
  if (!content.includes(`--${flag}`)) return undefined
  else {
    const input = content.split(`--${flag} `)[1].split(` --`)[0]
    return input
  }
}

module.exports = {
  time,
  capitalize,
  removeElement,
  trimArray,
  trimStringFromArray,
  getRange,
  getOrdinalNumeral,
  getCaseNumber,
  getStatus,
  replaceKeywords,
  replace_fm_variables,
  replace_all_variables,
  send_log_message,
  rotate,
  convert_embed_to_string,
  extract_color,
  flag,
  send_punishment
};