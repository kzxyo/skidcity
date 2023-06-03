const db = require('quick.db')

module.exports = (client, oldUser, newUser) => {
  if (oldUser.username != newUser.username || oldUser.discriminator != newUser.discriminator) {
    if (!db.get(`names_${newUser.id}`)) {
      db.set(`names_${newUser.id}`, [])
    }
    db.push(`names_${newUser.id}`, {
      name: newUser.tag,
      date: Date.now()
    })
    client.logger.info(`${oldUser.tag} user tag changed to ${newUser.tag} (${newUser.id})`);
  }
};