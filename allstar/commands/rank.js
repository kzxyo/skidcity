
const{ MessageEmbed,MessageAttachment } = require('discord.js');
const canvacord = require("canvacord");
const { default_prefix ,color,error,owner } = require("../config.json")
const db = require('quick.db')
const talkedRecently = new Set();
module.exports = {
	name: 'rank',
	description: 'returns user lvl in the server',
	aliases:['lvl','level'],
	usage: '\``` rank {user} \```',
  category: "utility",
	guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
  let pingemoji = `<:allstarconnection:996699189432025180>`

        if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {

      let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args.join(' ').toLocaleLowerCase()) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args.join(' ').toLocaleLowerCase()) || client.users.cache.get(args[0])

         if(!mentionedMember) {
   
   let xp = db.get(`xp_${message.guild.id}_${message.author.id}`)
   if(xp === null) xp = 0
   let ranks = db.get(`level_${message.guild.id}_${message.author.id}`)
   if(!ranks && ranks === null) ranks = 1
   let req = 100
   if(ranks === 0) req = 500
   if(ranks === 1) req = 1000
   if(ranks === 2) req = 2000
   if(ranks === 3) req = 4000
   if(ranks === 4) req = 5000
   if(ranks === 5) req = 7000
   if(ranks === 6) req = 9000
   if(ranks === 7) req = 12000
   if(ranks === 8) req = 15000
   if(ranks === 9) req = 18000
   if(ranks === 10) req = 20000
   if(ranks === 11) req = 24000
   if(ranks === 12) req = 28000
   if(ranks === 13) req = 33000
   if(ranks === 14) req = 38000
   if(ranks === 15) req = 44000
   if(ranks === 16) req = 50000
   if(ranks === 17) req = 55000
   if(ranks === 18) req = 60000
   if(ranks === 19) req = 70000
   if(ranks === 20) req = 85000
   if(ranks === 21) req = 100000
   if(ranks === 22) req = 120000
   if(ranks === 23) req = 150000
   if(ranks === 24) req = 200000
   if(ranks === 25) req = 250000
   if(ranks === 26) req = 300000
   if(ranks === 27) req = 350000
   if(ranks === 28) req = 400000
   if(ranks === 29) req = 450000
   if(ranks === 30) req = 550000
   if(ranks === 31) req = 650000
   if(ranks === 32) req = 800000
   if(ranks === 33) req = 950000
   if(ranks === 34) req = 1200000
   if(ranks === 35) req = 1500000
   if(ranks === 36) req = 2000000
   if(ranks === 37) req = 2500000
   if(ranks === 38) req = 3000000
   if(ranks === 39) req = 4500000
   if(ranks === 40) req = 6500000
   if(ranks === 41) req = 9000000
   if(ranks === 42) req = 10000000
   if(ranks === 43) req = 12000000
   if(ranks === 44) req = 15000000
   if(ranks === 45) req = 20000000
   if(ranks === 46) req = 25000000
   if(ranks === 47) req = 35000000
   if(ranks === 48) req = 55000000
   if(ranks === 49) req = 100000000

   let avatar = message.author.displayAvatarURL({dynamic:true})
   let username = message.author.username
  const rank = new canvacord.Rank()
    .setAvatar(avatar)
    .setCurrentXP(xp)
    .setRequiredXP(req)
    .setLevel(ranks,`Level`,true)
    .setRank(0,`.`,false)
    .setCustomStatusColor(color)
    .setUsername(username)
    .setProgressBar("#7289da", "COLOR")
    .setBackground("COLOR", `#000000`)
    .setDiscriminator(`${message.author.discriminator}`);

rank.build()
    .then(data => {
  let attachment = new MessageAttachment(data,"rankcard.png")
  message.reply({files:[attachment]})
        //canvacord.write(buffer, "RankCard.png");
    });
   
   
   
   
 }else {
   let xp = db.get(`activity_${message.guild.id}_${mentionedMember.user.id}`)
   if(xp === null) xp = 0
   let ranks = db.get(`level_${message.guild.id}_${mentionedMember.user.id}`)
   if(!ranks && ranks === null) ranks = 1
      let req = 100
      if(ranks === 0) req = 500
      if(ranks === 1) req = 1000
      if(ranks === 2) req = 2000
      if(ranks === 3) req = 4000
      if(ranks === 4) req = 5000
      if(ranks === 5) req = 7000
      if(ranks === 6) req = 9000
      if(ranks === 7) req = 12000
      if(ranks === 8) req = 15000
      if(ranks === 9) req = 18000
      if(ranks === 10) req = 20000
      if(ranks === 11) req = 24000
      if(ranks === 12) req = 28000
      if(ranks === 13) req = 33000
      if(ranks === 14) req = 38000
      if(ranks === 15) req = 44000
      if(ranks === 16) req = 50000
      if(ranks === 17) req = 55000
      if(ranks === 18) req = 60000
      if(ranks === 19) req = 70000
      if(ranks === 20) req = 85000
      if(ranks === 21) req = 100000
      if(ranks === 22) req = 120000
      if(ranks === 23) req = 150000
      if(ranks === 24) req = 200000
      if(ranks === 25) req = 250000
      if(ranks === 26) req = 300000
      if(ranks === 27) req = 350000
      if(ranks === 28) req = 400000
      if(ranks === 29) req = 450000
      if(ranks === 30) req = 550000
      if(ranks === 31) req = 650000
      if(ranks === 32) req = 800000
      if(ranks === 33) req = 950000
      if(ranks === 34) req = 1200000
      if(ranks === 35) req = 1500000
      if(ranks === 36) req = 2000000
      if(ranks === 37) req = 2500000
      if(ranks === 38) req = 3000000
      if(ranks === 39) req = 4500000
      if(ranks === 40) req = 6500000
      if(ranks === 41) req = 9000000
      if(ranks === 42) req = 10000000
      if(ranks === 43) req = 12000000
      if(ranks === 44) req = 15000000
      if(ranks === 45) req = 20000000
      if(ranks === 46) req = 25000000
      if(ranks === 47) req = 35000000
      if(ranks === 48) req = 55000000
      if(ranks === 49) req = 100000000

   let avatar = mentionedMember.displayAvatarURL({dynamic:true})
   let username = mentionedMember.user.username
  const rank = new canvacord.Rank()
    .setAvatar(avatar)
    .setCurrentXP(xp)
   .setRequiredXP(req)
      .setRank(0,`.`,false)
      .setCustomStatusColor(color)
     .setLevel(ranks,`Level`,true)
    .setProgressBar("#7289da", "COLOR")
       .setBackground("COLOR", `#000000`)
    .setUsername(username)
    .setDiscriminator(`${mentionedMember.user.discriminator}`);

rank.build()
    .then(data => {
  let attachment = new MessageAttachment(data,"rankcard.png")
  message.reply({files:[attachment]})
        //canvacord.write(buffer, "RankCard.png");
    });
   
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