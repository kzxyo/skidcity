const { MessageEmbed } = require("discord.js");
const { default_prefix ,color,error,owner } = require("../config.json")
const db = require('quick.db')
module.exports = {
  event: "messageCreate",
  execute: async (message, client) => {
    try {
    
        let prefis;
            let emoji = `<:887705796476018688:989122635705233418> `;
      let prefix = db.get(`prefix_${message.author.id}`)
      if (prefix === null) prefix = db.get(`prefix_${message.guild.id}`) 
      if (prefix === null) prefix = default_prefix;
  const args = message.content.slice(prefix.length).split(/ +/);
  let mentionFix = message.content.match(new RegExp(`^<@!?(${client.user.id})>`,"gi"))
  if (mentionFix) {
    prefis = `${mentionFix[0]}`
  }
    
  if (message.author.bot) return;
  if(db.get(`mocklock_${message.author.id}`)) {
    return;
  }
  if (message.content === 'allstar') {
          let serverfix = db.get(`prefix_${message.guild.id}`)
      if(serverfix === null) serverfix = `Not Set`
      let userfix = db.get(`prefix_${message.author.id}`)
      if(userfix === null) userfix = `Not Set`
      
    let mentionedMember =  message.member;
      const prefixEmbed = new MessageEmbed()
        .setDescription(`<:Settings:1032717784456626226>   **Prefixes For ${message.author.username}** \n> Default Prefix: \`${default_prefix}\` \n> Server prefix: \`${serverfix || `Not Set`}\` \n> Custom Prefix: \`${userfix || "Not Set"}\``)
        .setColor(color)   


    message.reply({embeds:[prefixEmbed]}).catch(() => {/*Ignore error*/})
  }
    else if(message.content.startsWith(`allstar`)){
      
      const args = message.content.slice('allstar'.length).split(/ +/);
      args.shift().toLowerCase();
      const commandName = args[0].toLowerCase();
      const command =
        client.commands.get(commandName) ||
        client.commands.find(
          (cmd) => cmd.aliases && cmd.aliases.includes(commandName)
        );
        args.shift()

        try {
          let blacklisted = db.get(`blacklisted`)
if(blacklisted && blacklisted.find(find => find.user == message.author.id)) {
return;
}
    let trustedusers = db.get(`privacy`)
if(trustedusers && trustedusers.find(find => find.user == message.author.id)) {
let cp = db.get(`commandsused`)
db.set(`commandsused`,cp + 1)
// console.log(message.content)
command.execute(message,args,client)
}
else {
        const row = new MessageActionRow().addComponents(
   new MessageButton()
    .setCustomId('yes')
    .setEmoji("<:Blurple_check:1013176396861931630>")
    .setStyle('SECONDARY'),
  
  new MessageButton()
    .setCustomId('no')
    .setEmoji("<:DW_X_Mark:1013176426763145216>")
    .setStyle('SECONDARY')
)
let msg = message.reply({embeds:[
  new MessageEmbed().setDescription(`Do you agree to allstars [Privacy policy](https://nekokouri.gitbook.io/allstar/details/privacy-policy) \n **Warning** Reacting with ${xmark} will blacklist you from using allstar`).setColor(color)
],
               components:[row]
              })
// const filter = (i) => {
//    if(i.author.id === message.author.id) return true
//  }

const collector = message.channel.createMessageComponentCollector({
  filter: i => i.user.id === message.author.id,
  max:1
})

collector.on("end", (ButtonInteraction) => {
 
  const id = ButtonInteraction.first().customId;
  if(id === 'yes') {
    
            let trustedusers = db.get(`privacy`)
if(trustedusers && trustedusers.find(find => find.user == message.author.id)) {
let trust = new MessageEmbed()
.setColor(error)
.setDescription(`${xmark} That user is already whitelisted`)
return message.reply({embeds:[trust]})
}
let data = {
user: message.author.id
}
db.push(`privacy`, data)
let added = new MessageEmbed()
.setDescription(`
${checked}  You accepted to allstars privacy policy
`)
.setColor(color)

return message.reply({
  embeds: [added]
});

    
    
    
    
  }
  if(id === 'no') {
    let data = {
user: message.author.id
}
    db.push(`blacklisted`,data)
 let embed = new MessageEmbed()
.setColor(color)
  message.channel.send({embeds:[
    new MessageEmbed().setDescription(`${xmark} now you'll be blacklisted from using commands`).setColor(color)
  ]})
  }
})

}

console.log(`Comamnd ran by un authorized user ${message.author.tag} command : ${command.name} Time : ${Date.now()} Server : ${message.guild.name}`)


// command.execute(message, args, client);
} catch (error) {
//console.error(error);
}
    }
      } catch{}

    
  },
};