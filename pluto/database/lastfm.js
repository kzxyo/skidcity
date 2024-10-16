const mongoose = require("mongoose")

const lastfmuserschema = new mongoose.Schema({
  UserID: String,
  Username: String,
});

module.exports = mongoose.model("fmuser", lastfmuserschema)