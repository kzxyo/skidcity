const { MessageEmbed } = require("discord.js");

const { default_prefix ,color,error,owner,xmark ,checked} = require("../config.json")
const db = require('quick.db')
module.exports = {
  event: "userUpdate",
  execute: async (o,n, client) => {
  
    
    if(o.tag === n.tag)  return;
      
      const style = 'R' 
    const starttime = `<t:${Math.floor(Date.now()/1000)}` + (style ? `:${style}` : '') + '>'
starttime
    let data = {
    name: {
      oldName:o.tag,
      time:starttime
    }
}
    db.push(`names_${n.id}`, data)
    const database = db.get(`names_${n.id}`)

  },
};