const mongoose = require('mongoose')

const globaldataschema = new mongoose.Schema({
  GuildID: String,
  Prefix: String,
  BlacklistedUsers: Array,
  AntiNukeToggle: String,
  AntiNukeChannel: String,
  AntiNukeWhitelistedUsers: Array,
  AntiNukeWhitelistedRoles: Array,
  WelcomeMessage: String,
  WelcomeChannel: String,
  GoodbyeMessage: String,
  GoodbyeChannel: String,
  AutoRoles: Array,
  JoinDM: String,
  AntiLink: String,
  FilteredWords: Array,
  Vanity: String,
  VanityMessage: String,
  VanityRoles: Array,
  VanityLogChannel: String
});

module.exports = mongoose.model('globaldata', globaldataschema)