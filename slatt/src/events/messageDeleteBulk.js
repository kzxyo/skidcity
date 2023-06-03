const db = require('quick.db')

module.exports = (client, messages) => {
    let num = 0
    db.set(`BulkSnipe_${messages.first().guild.id}`, messages.filter(m => m.content !== '').map(m => `\`${num++}\` ${m.author.tag}: **${m.content}**`))
};