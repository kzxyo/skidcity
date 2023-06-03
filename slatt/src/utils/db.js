const Sequelize = require('sequelize');
const sequelize = new Sequelize('database', 'user', 'password', {
    host: 'localhost',
    dialect: 'sqlite',
    logging: false,
    storage: 'database.sqlite',
});

const LastfmUsers = sequelize.define('users', { userID: { type: Sequelize.STRING, unique: true }, username: Sequelize.STRING })
LastfmUsers.sync();

const bans = sequelize.define('bans', { guildID: { type: Sequelize.STRING, unique: `ban` }, userID: { type: Sequelize.STRING, unique: `ban` } })
bans.sync()

const crowns = sequelize.define('crowns', { guildID: { type: Sequelize.STRING, unique: `crown` }, userID: Sequelize.STRING, artistName: { type: Sequelize.STRING, unique: `crown` }, artistPlays: Sequelize.INTEGER })
crowns.sync()


const prefix = sequelize.define('prefix', { guildID: { type: Sequelize.STRING }, prefix: Sequelize.STRING })
prefix.sync()

const afk = sequelize.define('afk', { guildID: { type: Sequelize.STRING }, userID: { type: Sequelize.STRING }, content: Sequelize.STRING, time: Sequelize.STRING })
afk.sync()

const embed = sequelize.define('embed', { userID: { type: Sequelize.STRING }, code: Sequelize.STRING })
embed.sync()

const lf_color = sequelize.define('lf_color', { userID: { type: Sequelize.STRING }, color: Sequelize.STRING })
lf_color.sync()

const autorole = sequelize.define('autorole', { guildID: { type: Sequelize.STRING }, role: Sequelize.STRING, })
autorole.sync()

const boost_channel = sequelize.define('boost_channel', { guildID: { type: Sequelize.STRING }, channel: Sequelize.STRING })
boost_channel.sync()

const boost_message = sequelize.define('boost_message', { guildID: { type: Sequelize.STRING }, message: Sequelize.STRING })
boost_message.sync()

const media_channel = sequelize.define('media_channel', { guildID: { type: Sequelize.STRING }, channelID: { type: Sequelize.STRING }, channel: Sequelize.STRING })
media_channel.sync()

const welcome_channel = sequelize.define('welcome_channel', { guildID: { type: Sequelize.STRING }, channel: Sequelize.STRING })
welcome_channel.sync()

const welcome_embed = sequelize.define('welcome_embed', { guildID: { type: Sequelize.STRING }, code: Sequelize.STRING })
welcome_embed.sync()

const welcome_message = sequelize.define('welcome_message', { guildID: { type: Sequelize.STRING }, message: Sequelize.STRING })
welcome_message.sync()

const mute_role = sequelize.define('mute_role', { guildID: { type: Sequelize.STRING }, role: Sequelize.STRING })
mute_role.sync()

const vanity_role = sequelize.define('vanity_role', { guildID: { type: Sequelize.STRING }, role: Sequelize.STRING })
vanity_role.sync()

const vanity_message = sequelize.define('vanity_message', { guildID: { type: Sequelize.STRING }, message: Sequelize.STRING })
vanity_message.sync()

const vanity_status = sequelize.define('vanity_status', { guildID: { type: Sequelize.STRING }, status: Sequelize.STRING })
vanity_status.sync()

const vanity_channel = sequelize.define('vanity_channel', { guildID: { type: Sequelize.STRING }, channel: Sequelize.STRING })
vanity_channel.sync()

const starboard = sequelize.define('starboard', { guildID: { type: Sequelize.STRING }, channel: Sequelize.STRING })
starboard.sync()

const starboard_emoji = sequelize.define('starboard_emoji', { guildID: { type: Sequelize.STRING }, emoji: Sequelize.STRING, emoji_id: Sequelize.STRING })
starboard_emoji.sync()

const reaction_history = sequelize.define('reaction_history', { guildID: { type: Sequelize.STRING }, messageID: { type: Sequelize.STRING }, reaction: Sequelize.STRING, author: Sequelize.STRING })
reaction_history.sync()

const jail_role = sequelize.define('jail_role', { guildID: { type: Sequelize.STRING }, role: Sequelize.STRING })
jail_role.sync()

const jail_channel = sequelize.define('jail_channel', { guildID: { type: Sequelize.STRING }, channel: Sequelize.STRING })
jail_channel.sync()

const jail_message = sequelize.define('jail_message', { guildID: { type: Sequelize.STRING }, message: Sequelize.STRING })
jail_message.sync()

const jailed = sequelize.define('jailed', { userID: { type: Sequelize.STRING }, guildID: { type: Sequelize.STRING } })
jailed.sync()

const muted = sequelize.define('muted', { userID: { type: Sequelize.STRING }, guildID: { type: Sequelize.STRING } })
muted.sync()

const lastfm_embed = sequelize.define('lastfm_embed', { userID: { type: Sequelize.STRING } })
lastfm_embed.sync()

const custom_fm = sequelize.define('custom_fm', { userID: { type: Sequelize.STRING } })
custom_fm.sync()

const custom_prefix = sequelize.define('custom_prefix', { userID: { type: Sequelize.STRING } })
custom_prefix.sync()

const badge = sequelize.define('badge', { userID: { type: Sequelize.STRING } })
badge.sync()

const updates = sequelize.define('updates', { guildID: { type: Sequelize.STRING }, channelID: {type: Sequelize.STRING} })
updates.sync()

const toggled_commands = sequelize.define('toggled_commands', { guildID: { type: Sequelize.STRING }, cmd: {type: Sequelize.STRING} })
toggled_commands.sync()

const command_whitelists = sequelize.define('command_whitelists', { guildID: { type: Sequelize.STRING }, cmd: {type: Sequelize.STRING}, userID: {type: Sequelize.STRING} })
command_whitelists.sync()

const history = sequelize.define('history', { 
    guildID: { type: Sequelize.STRING }, 
    userID: {type: Sequelize.STRING}, 
    action: {type: Sequelize.STRING}, 
    reason: {type: Sequelize.STRING},
    author: {type: Sequelize.STRING},
    date: {type: Sequelize.STRING},
    num: {type: Sequelize.INTEGER},
})
history.sync()
module.exports = {
    LastfmUsers, bans, crowns,
    prefix,
    afk,
    embed, lf_color,
    autorole,
    boost_channel, boost_message,
    media_channel,
    welcome_channel, welcome_message, welcome_embed,
    mute_role,
    vanity_role, vanity_message, vanity_status, vanity_channel,
    starboard, starboard_emoji,
    jail_message, jail_channel, jail_role, jailed,
    muted,
    lastfm_embed, custom_fm, custom_prefix, badge,
    updates,
    toggled_commands,
    command_whitelists,
    history,
}

