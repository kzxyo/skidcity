const { readdirSync } = require("fs");

module.exports = (client) => {

  readdirSync("./events/").forEach(file => {
      const events = readdirSync(`./events/`).filter(files => files.endsWith(".js"));

      for (let files of events) {
          let pull = require(`../events/${files}`);

      if (pull.name) {
        client.events.set(pull.name, pull);
      } else {
        continue;
      }
    }
  })
}