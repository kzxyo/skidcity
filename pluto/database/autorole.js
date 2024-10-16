const mongoose = require("mongoose")

const autoroleschema = new mongoose.Schema({
  GuildID: String,
  RoleID: String,
});

module.exports = mongoose.model("autorole", autoroleschema)