
const{ MessageEmbed,MessageActionRow,MessageButton } = require('discord.js');
const { default_prefix ,color,error,owner } = require("../config.json")
const moment = require('moment');
const talkedRecently = new Set();
module.exports = {
	name: 'userinfo',
	description: 'shows mentioned users info ',
	aliases:["whois"],
	usage: ' \```YAML\n\n whois @heist#0001 \``` ',
  category: "information",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
    let emoji = `<:allstar:1001031487103193108> `;
         let statusemoji = `<:allstaronline:998561463490850826> `
        

            if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {
      try {

        let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || client.users.cache.get(args[0])

        let rolemap = message.guild.members.cache.get(mentionedMember.id).roles.cache
        .sort((a, b) => b.position - a.position)
        .map(r => r)
        .join(",") 
       // if (!mentionedMember.permissions.has([ Permissions.FLAGS.ADMINISTRATOR]))  perms = `${`${mentionedMember.permissions.toArray().sort((a, b) => a.localeCompare(b)).map(p=> `\`${p}\``).join(", ")}`}`
  

       
         let perms = `${mentionedMember.permissions.toArray().sort((a, b) => a.localeCompare(b)).map(p=> p).join(",")}`
         perms = perms.replace('ADD_REACTIONS,','')
        perms = perms.replace('ATTACH_FILES,','')
        perms = perms.replace('CHANGE_NICKNAME,','')
        perms = perms.replace('CONNECT,','')
        perms = perms.replace('CREATE_INSTANT_INVITE,','')
        perms = perms.replace('CREATE_PRIVATE_THREADS,','')
        perms = perms.replace('CREATE_PUBLIC_THREADS,','')
        perms = perms.replace('EMBED_LINKS,',' ')
        perms = perms.replace('READ_MESSAGE_HISTORY,','')
        perms = perms.replace('REQUEST_TO_SPEAK,','')
        perms = perms.replace('SEND_MESSAGES,','')
        perms = perms.replace('SEND_MESSAGES_IN_THREADS,','')
        perms = perms.replace('SPEAK,',' ')
        perms = perms.replace('START_EMBEDDED_ACTIVITIES,','')
        perms = perms.replace('STREAM,',' ')
        perms = perms.replace('USE_APPLICATION_COMMANDS,','')
        perms = perms.replace('USE_EXTERNAL_EMOJIS,','')
        perms = perms.replace('USE_EXTERNAL_STICKERS,','')
        perms = perms.replace('USE_PRIVATE_THREADS,','')
        perms = perms.replace('USE_PUBLIC_THREADS,','')
        perms = perms.replace('USE_VAD,','')
        perms = perms.replace('VIEW_CHANNEL,','')

        let joinPos = Array.from(message.guild.members.cache).map(x => x = x[1]).sort((a, b) => a.joinedAt - b.joinedAt)
   
        let embed = new MessageEmbed()
        .setTitle(`${mentionedMember.user.username} ${mentionedMember.presence.status.replace('dnd','<:dndsssss:1032192241546035260>').replace('idle','<:idles:1032192245933277264>').replace('online','<:online:1032192253772435457> ').replace('offline','<:offline:1032192252811939930>')} \`${mentionedMember.user.id}\``)
        .setThumbnail(mentionedMember.user.displayAvatarURL({dynamic:true, size:4096}))
        .setFooter({text:`Join position ${joinPos.findIndex(obj => obj.user.id === mentionedMember.id) === 0 ? 1 : joinPos.findIndex(obj => obj.user.id === mentionedMember.id)}`})
        .setColor(color)
        .addFields(
        {
            name:`User Tag`,
            value: `${emoji} ${mentionedMember.user.tag}`,
            inline:true,
        },
        {
            name:`Joined`,
            value:`${emoji} <t:${parseInt(mentionedMember.joinedTimestamp/ 1000)}:R>`,
            inline: true,
        },
        {
            name:`Created`,
           // value: `<:allstartime:997233251695480873>  ${moment(mentionedMember.createdAt).format("dddd MMMM YYYY")}`,
            value: `${emoji} <t:${parseInt(mentionedMember.user.createdTimestamp / 1000, 10)}:R>`,
            inline: true,
        },
        { 
          name:`Highest Role`,
          value:`${emoji} ${mentionedMember.roles.highest}`,
          inline:true,
          
        },
       
            )
        .addField(`Roles [${message.guild.members.cache.get(mentionedMember.id).roles.cache.size || "0"}]`,` ${rolemap || "0"}`)
       // .addField(`Permissions`,'\```YAML\n' + perms + '\```')

        message.reply({embeds:[embed]});
      
      
      } catch(error){ }
	}
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};