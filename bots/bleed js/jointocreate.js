const config = require("./config");
const jointocreatemap = new Map();
module.exports = function (client) {
  const description = {
    name: "jointocreate",
    filename: "jointocreate.js",
    version: "3.2"
  }
  new Promise(resolve => {
    setInterval(() => {
      resolve(2);
      try {
        const guild = client.guilds.cache.get(config.guildid);
        const channels = guild.channels.cache.map(ch => ch.id)
        for (let i = 0; i < channels.length; i++) {
          const key = `tempvoicechannel_${guild.id}_${channels[i]}`;
          if (jointocreatemap.get(key)) {
            var vc = guild.channels.cache.get(jointocreatemap.get(key));
            if (vc.members.size < 1) {
              jointocreatemap.delete(key);
              return vc.delete();
            } else { }
          }
        }
      } catch { }
    }, 10000)
  })


  client.on("voiceStateUpdate", (oldState, newState) => {

    let oldparentname = "unknown"
    let oldchannelname = "unknown"
    let oldchanelid = "unknown"
    if (oldState && oldState.channel && oldState.channel.parent && oldState.channel.parent.name) oldparentname = oldState.channel.parent.name
    if (oldState && oldState.channel && oldState.channel.name) oldchannelname = oldState.channel.name
    if (oldState && oldState.channelID) oldchanelid = oldState.channelID
    let newparentname = "unknown"
    let newchannelname = "unknown"
    let newchanelid = "unknown"
    if (newState && newState.channel && newState.channel.parent && newState.channel.parent.name) newparentname = newState.channel.parent.name
    if (newState && newState.channel && newState.channel.name) newchannelname = newState.channel.name
    if (newState && newState.channelID) newchanelid = newState.channelID
    if (oldState.channelID) {
      if (typeof oldState.channel.parent !== "undefined") oldChannelName = `${oldparentname}\n\t**${oldchannelname}**\n*${oldchanelid}*`
      else oldChannelName = `-\n\t**${oldparentname}**\n*${oldchanelid}*`
    }
    if (newState.channelID) {
      if (typeof newState.channel.parent !== "undefined") newChannelName = `${newparentname}\n\t**${newchannelname}**\n*${newchanelid}*`
      else newChannelName = `-\n\t**${newchannelname}**\n*${newchanelid}*`
    }

    if (!oldState.channelID && newState.channelID) {
      if (newState.channelID !== config.JOINTOCREATECHANNEL) return;
      jointocreatechannel(newState);
    }
    if (oldState.channelID && !newState.channelID) {
      if (jointocreatemap.get(`tempvoicechannel_${oldState.guild.id}_${oldState.channelID}`)) {
        var vc = oldState.guild.channels.cache.get(jointocreatemap.get(`tempvoicechannel_${oldState.guild.id}_${oldState.channelID}`));
        if (vc.members.size < 1) {
          jointocreatemap.delete(`tempvoicechannel_${oldState.guild.id}_${oldState.channelID}`);
          return vc.delete();
        }
        else {
        }
      }
    }
    if (oldState.channelID && newState.channelID) {

      if (oldState.channelID !== newState.channelID) {
        if (newState.channelID === config.JOINTOCREATECHANNEL)
          jointocreatechannel(oldState);
        if (jointocreatemap.get(`tempvoicechannel_${oldState.guild.id}_${oldState.channelID}`)) {
          var vc = oldState.guild.channels.cache.get(jointocreatemap.get(`tempvoicechannel_${oldState.guild.id}_${oldState.channelID}`));
          if (vc.members.size < 1) {
            jointocreatemap.delete(`tempvoicechannel_${oldState.guild.id}_${oldState.channelID}`);
            return vc.delete();
          }
          else {
          }
        }
      }
    }
  })
  async function jointocreatechannel(user) {
    await user.guild.channels.create(`${user.member.user.username}'s room`, {
      type: 'voice',
      parent: user.channel.parent.id,
    }).then(async vc => {
      user.setChannel(vc);
      jointocreatemap.set(`tempvoicechannel_${vc.guild.id}_${vc.id}`, vc.id);
      await vc.overwritePermissions([
        {
          id: user.id,
          allow: ['MANAGE_CHANNELS'],
        },
        {
          id: user.guild.id,
          allow: ['VIEW_CHANNEL'],
        },
      ]);
    })
  }
}