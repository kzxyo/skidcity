module.exports = {
    name: "unban",
    aliases: [],
    run: async (client, message, args) => {
     if (!message.member.permissions.has("BAN_MEMBERS")) {
       message.channel.send({ content: `*${message.author.username},* you need **BAN_MEMBERS** permission to run that command.` });
     } else {
       const ID = args[0];
       if (!ID) {
         message.channel.send({ content: `usage: unban @user` });
       } else {
         const user = await message.guild.bans.fetch(ID);
         
         if (!user) {
           message.channel.send({ content: `that user is not banned from this guild` });
         } else {
           message.guild.members.unban(ID).catch(() => {
             message.channel.send(`could't find the ban`)
           })
           message.channel.send({ content: `:thumbsup:` });
         }
       }
     }
  },
};