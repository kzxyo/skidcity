module.exports = {
  name: "nick",
  aliases: ["nickname", "setnick"],
  run: async (client, message, args) => {
    const nickname = args[0];
    if (!message.member.permissions.has("MANAGE_MEMBERS")) {
      message.channel.send({ content: `*${message.author.username}*, you need **MANAGE_MEMBERS** permissions to do that`});
    } else {
      const member = message.mentions.members.first();
      if (!member) {
        message.channel.send({ content: `usage: nick <nickname> @user`});
      } 
      if (!member.manageable) {
        message.channel.send({ content: `im unable to manage that user` });
      } else {
        if (!nickname) {
          message.channel.send({ content: `usage: nick <nickname> @user` });
        } else {
        member.setNickname(`${nickname}`);
        message.channel.send({ content: `:thumbsup:`});
        }
      }
    }
  },
};