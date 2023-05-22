client.on("guildMemberUpdate", (oldMember, newMember) => {
  if(newMember.nickname && oldMember.nickname !== newMember.nickname) { 
    let nametag = db.fetch(`roleonname_name_${newMember.guild.id}`)
    let channeltag = db.fetch(`roleonname_channel_${newMember.guild.id}`)
    let roletag = db.fetch(`roleonname_role_${newMember.guild.id}`)
    if(newMember.user.username.includes(`${nametag}`)) {
        let role = newMember.guild.roles.cache.find(role => role.id == `${roletag}`)
        newMember.roles.add(role).catch(console.log("error on role add"))
        let channel = newMember.guild.channels.cache.find(channel => channel.id == `${channeltag}`)
        let mes = new Discord.MessageEmbed()
        .setColor(`2f3136`)
        .setDescription(`${newMember} thank you for having **${nametag}** in your name!`)
        channel.send(mes)
    } else {
      if(newMember.guild.roles.cache.find(r => r.id == `${roletag}`)) {
      let role = newMember.guild.roles.cache.find(role => role.id == `${roletag}`)
      newMember.roles.remove(role).catch(console.log("error on role remove"))
      let channel = newMember.guild.channels.cache.find(channel => channel.id == `${channeltag}`)
      let mesoof = new Discord.MessageEmbed()
      .setColor(`2f3136`)
      .setDescription(`${newMember} removed **${nametag}** from their name!`)
      channel.send(mes