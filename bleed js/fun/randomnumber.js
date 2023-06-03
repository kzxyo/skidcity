module.exports = {
  name: "randomnumber",
  aliases: ["rn"],

  run: async (client, message, args) => {

    let result = Math.floor(Math.random() * 101);

    message.channel.send(`${result}`);
  }
};