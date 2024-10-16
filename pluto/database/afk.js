const mongoose = require('mongoose')

const afkschema = new mongoose.Schema({
  GuildID: String,
  UserID: String,
  Message: String,
  TimeAgo: String
});

module.exports = mongoose.model('afk', afkschema)