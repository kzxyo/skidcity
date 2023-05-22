
const{ MessageEmbed,MessageAttachment,MessageActionRow,MessageButton } = require('discord.js');

const canvacord = require("canvacord");
const { default_prefix ,color,error,owner ,xmark} = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'spotify',
	description: '\```shows mentioned users current spotify status \```',
	aliases:[],
	usage: '\```spotify {user}',
  category: "utility",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
        if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {
    const toTimestamp = (strDate) => {
  const dt = Date.parse(strDate);
  return dt / 1000;
}

let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || client.users.cache.get(args[0])

if(!mentionedMember) mentionedMember = message.guild.members.cache.get(message.author.id)
            if(mentionedMember.presence == null) return message.reply({embeds:[new MessageEmbed().setDescription(`${xmark} That user is offline`).setColor(error)]})
      
      
            if(mentionedMember.presence.activities[0] === 'undefined') return  message.reply({embeds:[new MessageEmbed().setDescription(`${xmark} That user is not listening to spotify`).setColor(error)]})
           if(!mentionedMember.presence.activities[0]) return  message.reply({embeds:[new MessageEmbed().setDescription(`${xmark} That user is not listening to spotify`).setColor(error)]})
            if(mentionedMember.presence.activities[0].name === 'Spotify') {
              
              
            let trackIMG = `https://i.scdn.co/image/${mentionedMember.presence.activities[0].assets.largeImage.slice(8)}`;
            let trackURL = `https://open.spotify.com/track/${mentionedMember.presence.activities[0].syncId}`;
            let trackName = mentionedMember.presence.activities[0].details;
            let trackAuthor = mentionedMember.presence.activities[0].state;
            let trackAlbum = mentionedMember.presence.activities[0].assets.largeText;
            let style = 'R'
            let ends = `<t:${Math.floor(mentionedMember.presence.activities[0].timestamps.end/1000)}` + (style ? `:${style}` : '') + '>'
        
              const card = new canvacord.Spotify()
                  .setAuthor(trackAuthor)
                  .setAlbum(trackAlbum)
                  .setStartTimestamp(mentionedMember.presence.activities[0].timestamps.start)
                  .setEndTimestamp(mentionedMember.presence.activities[0].timestamps.end)
                  .setImage(trackIMG)
                  .setTitle(trackName);
               card.build()
                   .then(data => {
                    let attachment = new MessageAttachment(data,"spotify.png")
            const embed = new MessageEmbed()
                .setAuthor({name:`${mentionedMember.user.username} is listening `,iconURL:`${mentionedMember.user.displayAvatarURL({dynamic:true})}`})
                .setColor("GREEN")
                .setImage('attachment://spotify.png')
               // .setThumbnail(trackIMG)
              //  .addField('Spotify <:sspotify:1019692790910820482> ', `> **Track** :: [${trackName}](${trackURL}) \n> **Artist** :: ${mentionedMember.presence.activities[0].state}\n> **Album** :: ${trackAlbum} `,true)    //\n> **Ends** :: ${ends}`, true)
            
       const row = new MessageActionRow()

       .addComponents(
         new MessageButton()
         .setLabel('Listen here')
         .setEmoji("<:sspotify:1019692790910820482> ")
         .setURL(`${trackURL}`)
         .setStyle('LINK'),
        )
            message.reply({embeds:[embed],files:[attachment],components:[row]})
              .then(messageReact => {
                messageReact.react(`👍`)
                messageReact.react(`👎`)
            }) 
               })
              
            } else if(!mentionedMember.presence.activities[1]) return  message.reply({embeds:[new MessageEmbed().setDescription(`${xmark} That user is not listening to spotify`).setColor(error)]})
              
             else if(mentionedMember.presence.activities[1].name === 'Spotify'){
              
                            
            let trackIMG = `https://i.scdn.co/image/${mentionedMember.presence.activities[1].assets.largeImage.slice(8)}`;
            let trackURL = `https://open.spotify.com/track/${mentionedMember.presence.activities[1].syncId}`;
            let trackName = mentionedMember.presence.activities[1].details;
            let trackAuthor = mentionedMember.presence.activities[1].state;
            let trackAlbum = mentionedMember.presence.activities[1].assets.largeText;
            let style = 'R'
            let ends = `<t:${Math.floor(mentionedMember.presence.activities[1].timestamps.end/1000)}` + (style ? `:${style}` : '') + '>'
          
              const card = new canvacord.Spotify()
                  .setAuthor(trackAuthor)
                  .setAlbum(trackAlbum)
                  .setStartTimestamp(mentionedMember.presence.activities[1].timestamps.start)
                  .setEndTimestamp(mentionedMember.presence.activities[1].timestamps.end)
                  .setImage(trackIMG)
                  .setTitle(trackName);
               card.build()
                   .then(data => {
                    let attachment = new MessageAttachment(data,"spotify.png")
            const embed = new MessageEmbed()
                .setAuthor({name:`${mentionedMember.user.username} is listening `,iconURL:`${mentionedMember.user.displayAvatarURL({dynamic:true})}`})
                .setColor("GREEN")
             .setImage('attachment://spotify.png')
               // .setThumbnail(trackIMG)
               // .addField('Spotify <:sspotify:1019692790910820482> ', `> **Track** :: [${trackName}](${trackURL}) \n> **Artist** :: ${mentionedMember.presence.activities[1].state}\n> **Album** :: ${trackAlbum}  `,true)    //\n> **Ends** :: ${ends}`, true)
      const row = new MessageActionRow()

       .addComponents(
         new MessageButton()
         .setLabel('Listen here')
         .setEmoji("<:sspotify:1019692790910820482> ")
         .setURL(`${trackURL}`)
         .setStyle('LINK'),
        )
            message.reply({embeds:[embed],files:[attachment],components:[row]})
              .then(messageReact => {
                messageReact.react(`👍`)
                messageReact.react(`👎`)
            }) 
              
               })
              
              
              
              
              
              
            }else{
              message.reply({embeds:[
                new MessageEmbed()
                .setDescription(`${xmark} That user is not listening to spotify`)
                .setColor(error)
              ]})
              
            }
        
      


        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);

    }
    
	},
};


