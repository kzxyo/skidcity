const { Client, Message, MessageEmbed } = require ("discord.js");
const { approve } = require('../../emojis.json')
const glob = require("glob");
module.exports = {
name: "reload",
cooldowns: 10000,
/** 
 * @param {Client} client
 * @param {Message} message
 * @param {Stri ng[]} args
*/
run: async (client , message, args) => {
 
if (message.author.id !== "1137846765576540171") return;
client.commands.sweep(() => true)
glob(`${__dirname}/../**/*.js` , async (err, filePaths) => {
    if (err) return console.log(err);
    filePaths.forEach((file) => {
delete require.cache[require.resolve(file)];

const pull = require(file);
if(pull.name) {
    console.log(`Reloaded ${pull.name} (cmd)`);
    client.commands.set(pull.name, pull);
}

if(pull.aliases && Array.isArray(pull.aliases)) {
    pull.aliases.forEach((alias) => {
        
    client.aliases.set(alias, pull.name);
    });
}
    }); 
});

const embed = new MessageEmbed()
  
.setColor("#a3eb7b")
.setDescription(`${approve} ${message.author}: Sucessfully reloaded all commands`)

return message.channel.send({ embeds: [embed] })
}
}