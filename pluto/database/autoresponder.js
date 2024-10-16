const mongoose = require("mongoose")

const autoresponderschema = new mongoose.Schema({
  GuildID: String,
  Trigger: String,
  Response: String
});

module.exports = mongoose.model("autoresponder", autoresponderschema)