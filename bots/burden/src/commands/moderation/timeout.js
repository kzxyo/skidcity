module.exports = {
  name: "timeout",
  aliases: ["tm"],
  run: async (client, message, args) => {
    const member = message.mentions.members.first();
    if (!message.member.permissions.has("MANAGE_MESSAGES")) {
      message.channel.send({ content: `*${message.author.username}*, you need **MANAGE_MESSAGES** permission to do that.`});
    } else {
      if (!member) {
        message.channel.send({ content: `usage: timeout @user`});
      } 
      if (!member.manageable) {
        message.channel.send({ content: `i don't have access to manage this member.` });
      } else {
        if (member.isCommunicationDisabled()) {
          member.timeout(null);
          message.channel.send({ content: `:thumbsup:`});
        } else {
        member.timeout(10000000);
        message.channel.send({ content: `:thumbsup:`});
        }
      }
    }
  },
};