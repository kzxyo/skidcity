const client = require('../../index'),
  st = require('../../core/settings'),
  db = require('../../core/db.js');

/* On guild join */
client.on('guildCreate', async (guild) => {
  const isAllowed = st.bot.options.privateMode;
  if (isAllowed !== false) guild.leave();
});

/* On guild leave */
client.on('guildDelete', async (guild) => {
  db.list(`${guild.id}`).then((keys) => {
    keys.forEach(async (key) => {
      await db.delete(`${key}`)
    })
  });
});