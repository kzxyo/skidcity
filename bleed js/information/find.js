module.exports = {
  name: "find",

  run: async (client, message, args) => {
    let user = message.mentions.members.first() || message.guild.members.cache.get(args[0]);
    if (!user) user = message.member;

    if (user) {
      const mapped = client.guilds.cache.map(g => {
        if (g.members.cache.find(member => member.id === user.id)) return client.guilds.cache.size;
      });

      message.channel.send(`${user}: ${mapped} common servers`);
    }
  }
}