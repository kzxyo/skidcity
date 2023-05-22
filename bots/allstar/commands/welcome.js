 
const{ MessageEmbed,Permissions } = require('discord.js');
const db = require('quick.db')
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const request = require('request')
const talkedRecently = new Set();
module.exports = {
	name: 'welcome',
	description: 'welcomer setup to welcome new users ',
	aliases:["greet","welc"],
	usage: ' \```YAML\n\n greet channel {#channel} \n greet embed [on/off] \n greet message {text} \n greet footer {text} \n greet author {text} \n greet image {image} \n greet removeimage \n greet clear \n greet stats \n greet variables \n greet color {color} \``` ',
	category: "welcome/goodbye",
  guildOnly: false,
	args: false,
	permissions: {
		bot: [],
		user: [],
	},
	execute: async(message, args, client) => {
    
     let emoji = `<:allstarreply:1032192256192553030>`;
                if (talkedRecently.has(message.author.id)) {
             message.react(`⌛`)
    } else {

    let missperms = new MessageEmbed()
    .setDescription(`${xmark} You're missing \`MANAGE_GUILD\` permission`)
    .setColor(error)
    if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_GUILD])) return message.reply({ embeds:[missperms]});

    let prefix = db.get(`prefix_${message.guild.id}`);
    if (prefix === null) { prefix = default_prefix; };
    if (message.author.bot) return;
    const embed = new MessageEmbed()
      .setDescription(`\<a:allstarwelcome:996512695480238182>  **greet setup** \n <:allstar:1001031487103193108> greet channel \n <:allstar:1001031487103193108> greet embed <:allstar:1001031487103193108> greet message \n <:allstar:1001031487103193108> greet footer \n <:allstar:1001031487103193108> greet author \n <:allstar:1001031487103193108> greet image \n <:allstar:1001031487103193108> greet removeimage \n <:allstar:1001031487103193108> greet clear \n <:allstar:1001031487103193108> greet stats \n <:allstar:1001031487103193108> greet variables \n <:allstar:1001031487103193108> greet color`)
      .setColor(color)

    if (!args[0]) {
      message.reply({embeds:[embed]})
    } 
    if (args[0] === 'message') {
      db.set(`welmessage_${message.guild.id}`, args.splice(1).join(' '))
      let wlcmsg = db.get(`welmessage_${message.guild.id}`)
      if (wlcmsg === null) {
        const setmsgembed = new MessageEmbed()
          .setDescription(`${xmark} There is no welcome message set one with ${prefix}welcome message`)
          .setColor(error)
        return message.reply({embeds:[setmsgembed]})
      } else {
        const setembed = new MessageEmbed()
          .setTitle(`${checked} welcome message updated`)
          .setDescription(`${wlcmsg}`)
          .setColor(color)
        return message.reply({embeds:[setembed]})
      }
    } else if (args[0] === 'test') {
      let chx = db.get(`welchannel_${message.guild.id}`);
      if (chx === null) {
        let nochan = new MessageEmbed()
          .setDescription(`${xmark} There is no welcome channel set`)
          .setColor(error)
        
        return message.reply({embeds:[nochan]})
      }
      let welcome = db.get(`welmessage_${message.guild.id}`);
      if (welcome === null) {
                const setmsgembed = new MessageEmbed()
          .setDescription(`${xmark} There is no welcome message set one with ${prefix}welcome message`)
          .setColor(error)
        return message.reply({embeds:[setmsgembed]})
      }
      let footer = db.get(`welcembed_${message.guild.id}`);
      if (footer === null) { footer = `` }
      let image = db.get(`image_${message.guild.id}`)
      if (image === null) {
        //image = `https://cdn.discordapp.com/attachments/989999587890712606/990905254138765362/Screenshot_7.png`
      } 
      let author = db.get(`author_${message.guild.id}`)
      if (author === null) {
        author = ""
      }
       let colors = db.get(`color_${message.guild.id}`) 
       if(colors === null) {
         colors = color;
       }
      let thumbnail = db.get(`thumbnail_${message.guild.id}`)
      if(thumbnail === null) {
        thumbnail = ` `
      }
      if(thumbnail === '')
      
      if(thumbnail)thumbnail = thumbnail.replace('{user.icon}', message.member.displayAvatarURL({dynamic:true}));
      if(thumbnail)thumbnail = thumbnail.replace('{guild.icon}', message.guild.iconURL({dynamic:true}));
      if(image)image = image.replace('{user.icon}', message.member.displayAvatarURL({dynamic:true}));
      if(image)image = image.replace('{guild.icon}', message.guild.iconURL({dynamic:true}));

      welcome = welcome.replace('{user}', message.member);
      welcome = welcome.replace('{user.name}', message.author.username);
      welcome = welcome.replace('{user.tag}', message.author.tag);
      welcome = welcome.replace('{user.id}', message.author.id);
      welcome = welcome.replace('{membercount}', message.member.guild.memberCount);
      const ordinal = (message.guild.memberCount.toString().endsWith(1) && !message.guild.memberCount.toString().endsWith(11)) ? 'st' : (message.guild.memberCount.toString().endsWith(2) && !message.guild.memberCount.toString().endsWith(12)) ? 'nd' : (message.guild.memberCount.toString().endsWith(3) && !message.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
      welcome = welcome.replace('{membercount.ordinal}', message.member.guild.memberCount + ordinal);
      welcome = welcome.replace('{guild.name}', message.member.guild.name);
      welcome = welcome.replace('{guild.id}', message.member.guild.id);

      footer  = footer.replace('{user}', message.member);
      footer  = footer.replace('{user.name}', message.author.username);
      footer  = footer.replace('{user.tag}', message.author.tag);
      footer  = footer.replace('{user.id}', message.author.id);
      footer  = footer.replace('{membercount}', message.member.guild.memberCount);
      footer  = footer.replace('{membercount.ordinal}', message.member.guild.memberCount + ordinal);
      footer  = footer.replace('{guild.name}', message.member.guild.name);
      footer  = footer.replace('{guild.id}', message.member.guild.id);
      
      author = author.replace('{user}', message.member);
      author = author.replace('{user.name}', message.author.username);
      author = author.replace('{user.tag}', message.author.tag);
      author = author.replace('{user.id}', message.author.id);
      author = author.replace('{membercount}', message.member.guild.memberCount);
      author = author.replace('{membercount.ordinal}', message.member.guild.memberCount + ordinal);
      author = author.replace('{guild.name}', message.member.guild.name);
      author = author.replace('{guild.id}', message.member.guild.id);
      if(thumbnail === '{user.icon}') thumbnail =  message.member.displayAvatarURL({dynamic:true})
      let tested = new MessageEmbed()
      .setDescription(`${checked} Tested welcomer in <#` + chx + `>` )
      .setColor(color)
      console.log(thumbnail)
      let welcembed = new MessageEmbed()

      .setDescription(welcome)
      .setAuthor({name:`${author}`})
      //.setColor(0x2f3136)
      .setColor(colors || 0x2f3136)
     // .setThumbnail(`${thumbnail}`)
      .setThumbnail(thumbnail || message.member.displayAvatarURL({dynamic:true,size:4096}))
      //if (image)  welcembed.setImage(image)
      .setImage(image)
      .setFooter({text:`${footer}`})
      let em = db.get(`embedoff_${message.guild.id}`)
      if(em) {
        
      
      return client.channels.cache.get(chx).send({content:`${message.author}`,embeds:[welcembed]}).catch((error) =>{return message.reply(error)}).then(() => message.channel.send({embeds:[tested]}))
      } else  {
        return client.channels.cache.get(chx).send({content:`${welcome}`}).then(() => message.channel.send({embeds:[tested]}))
      }
        
      if (chx === null) {
        let chxnull = new MessageEmbed()
        .setDescription(`${xmark} There is no welcome channel set`)
        .setColor(error)
        return message.reply({embeds:[chxnull]})
      }
    } else if (args[0] === 'variables') {
      const member = message.author
      const ordinal = (message.guild.memberCount.toString().endsWith(1) && !message.guild.memberCount.toString().endsWith(11)) ? 'st' : (message.guild.memberCount.toString().endsWith(2) && !message.guild.memberCount.toString().endsWith(12)) ? 'nd' : (message.guild.memberCount.toString().endsWith(3) && !message.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
      const variablesembed = new MessageEmbed()
        .setTitle(`welcome variables`)
        .setDescription(`> {user}  - <@` + member + `>\n> {user.name}  - ` + message.author.username + `\n> {user.tag}  - ` + message.author.tag + `\n> {user.id}  - ` + message.author.id + `\n> {guild.name}  - ` + message.member.guild.name + `\n> {guild.id}  - ` + message.member.guild.id + `\n> {membercount}  - ` + message.member.guild.memberCount + `\n> {membercount.ordinal}  - ` + message.member.guild.memberCount + ordinal + `\n **Image Variables**  \n> {guild.icon}\n {user.icon}`)
        .setColor(color)
      message.reply({embeds:[variablesembed]})
    } else if (args[0] === "channel") {
      let channel = message.mentions.channels.first()
      if (!channel) {
        const welcomechannel = new MessageEmbed()
        .setDescription(`${xmark} you need to mention a channel set the channel to welcome new users \n> welcome channel <:allstarchannell:996785609777614918> channel`)
        .setColor(error)
        return message.reply({embeds:[welcomechannel]})
      }
      db.set(`welchannel_${message.guild.id}`, channel.id)
      let xs = new MessageEmbed()
      .setDescription(`${checked} Set the welcome channel to ${channel}`)
      .setColor(color)
      await message.reply({embeds:[xs]})
    }  else if (args[0] === "clear") {
      let deleted = new MessageEmbed()
      .setDescription(`${checked} cleared welcome setup from the database`)
      .setColor(color)
      db.delete(`welchannel_${message.guild.id}`)
      db.delete(`welcembed_${message.guild.id}`);
      db.delete(`welmessage_${message.guild.id}`)
      db.delete(`image_${message.guild.id}`)
      db.delete(`author_${message.guild.id}`)
      db.delete(`color_${message.guild.id}`)
      db.delete(`thumbnail_${message.guild.id}`)
      return await message.reply({embeds:[deleted]})
    }
    else if(args[0] === "footer"){
      db.set(`welcembed_${message.guild.id}`, args.splice(1).join(' '))
        let footers = db.get(`welcembed_${message.guild.id}`);
      if (footers === null) return;
      let footemebed = new MessageEmbed()
      .setTitle(`${checked} sucessfuly updated footer`)
       .setDescription(`${footers}`)
      return await message.reply({embeds:[footemebed]})

    }

    else if(args[0] === "image") {
        if(args[1] === '{guild.icon}'){
                  let x = new MessageEmbed()
        .setDescription(`${checked} Succesfully updated Image`)
        .setColor(color)
         db.set(`image_${message.guild.id}`,args[1])
        message.reply({embeds:[x]})
       
        }
        else if(args[1]== '{user.icon}') {
                            let x = new MessageEmbed()
        .setDescription(`${checked} Succesfully updated Image`)
        .setColor(color)
         db.set(`image_${message.guild.id}`,args[1])
        return message.reply({embeds:[x]})
        } else {
          
        
        let icon = args[1]
      //  if(!icon) icon = args[0]
      let no = new MessageEmbed()
      .setDescription(`${xmark} Not a well formed URL`)
      .setColor(error)
        let x = new MessageEmbed()
        .setDescription(`${checked} Succesfully updated Image`)
        .setColor(color)
        
                if (message.attachments.first()) {
      icon = message.attachments.first().url
         console.log(icon)
      db.set(`image_${message.guild.id}`, icon || args[1])
        return message.reply({embeds:[x]})
      .catch(() => {
        message.reply({embeds:[no]})
        
      })
    } 
        }
 
    }
      else if(args[0] === "removeimage") {
        let x = new MessageEmbed()
        .setDescription(`${checked} sucessfuly removed image`)
        .setColor(color)

            db.delete(`image_${message.guild.id}`)
      return await message.reply({embeds:[x]})
 
    } else if(args[0] === "stats") {
  
      let footers = db.get(`welcembed_${message.guild.id}`);
      if (footers === null) footers = 'Not Set';
      
      let welcome = db.get(`welmessage_${message.guild.id}`)
      if (welcome === null)   welcome = 'Not Set'
      
     let chx = db.get(`welchannel_${message.guild.id}`);
      if (chx) chx = `<#${chx}>`
      else if (chx === null) chx = `Not Set`
      
      let image = db.get(`image_${message.guild.id}`)
      if(image) image = `[Image](${image})` 
      else if (image === null) image = 'Not Set'
      let author = db.get(`author_${message.guild.id}`)
      if (author === null) {
        author = "Not Set"
      }
      let colors = db.get(`color_${message.guild.id}`)
      if (colors === null) colors = "Not Set"
            let thumbnail = db.get(`thumbnail_${message.guild.id}`)
            if(thumbnail) thumbnail = `[Thumbnail](${thumbnail})` 
      else if(thumbnail === null) {
        thumbnail = "Not Set"
      }
      let em = db.get(`embedoff_${message.guild.id}`)
      if(em == true){
        em === `Enabled`
      }
      else if(em === null){
        em === `Enabled`
      }
      welcome = welcome.replace('{user}', message.member);
      welcome = welcome.replace('{user.name}', message.author.username);
      welcome = welcome.replace('{user.tag}', message.author.tag);
      welcome = welcome.replace('{user.id}', message.author.id);
      welcome = welcome.replace('{membercount}', message.member.guild.memberCount);
      const ordinal = (message.guild.memberCount.toString().endsWith(1) && !message.guild.memberCount.toString().endsWith(11)) ? 'st' : (message.guild.memberCount.toString().endsWith(2) && !message.guild.memberCount.toString().endsWith(12)) ? 'nd' : (message.guild.memberCount.toString().endsWith(3) && !message.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
      welcome = welcome.replace('{membercount.ordinal}', message.member.guild.memberCount + ordinal);
      welcome = welcome.replace('{guild.name}', message.member.guild.name);
      welcome = welcome.replace('{guild.id}', message.member.guild.id);

      footers  = footers.replace('{user}', message.member);
      footers  = footers.replace('{user.name}', message.author.username);
      footers  = footers.replace('{user.tag}', message.author.tag);
      footers  = footers.replace('{user.id}', message.author.id);
      footers  = footers.replace('{membercount}', message.member.guild.memberCount);
      footers  = footers.replace('{membercount.ordinal}', message.member.guild.memberCount + ordinal);
      footers  = footers.replace('{guild.name}', message.member.guild.name);
      footers  = footers.replace('{guild.id}', message.member.guild.id);
      
      author = author.replace('{user}', message.member);
      author = author.replace('{user.name}', message.author.username);
      author = author.replace('{user.tag}', message.author.tag);
      author = author.replace('{user.id}', message.author.id);
      author = author.replace('{membercount}', message.member.guild.memberCount);
      author = author.replace('{membercount.ordinal}', message.member.guild.memberCount + ordinal);
      author = author.replace('{guild.name}', message.member.guild.name);
      author = author.replace('{guild.id}', message.member.guild.id);
         thumbnail = thumbnail.replace('{guild.icon}',message.guild.iconURL({dynamic:true,size:4096}))
    thumbnail = thumbnail.replace('{user.icon}',message.member.displayAvatarURL({dynamic:true,size:4096}))
      image = image.replace('{guild.icon}',message.guild.iconURL({dynamic:true,size:4096}))
    image = image.replace('{user.icon}',message.author.displayAvatarURL({dynamic:true,size:4096}))
      
      
      let stats = new MessageEmbed()
      .setDescription(`<a:allstarwelcome:996512695480238182> ${message.guild.name} Welcome Stats `)
      .setColor(color)
            .addFields({
        name:`Welcome Channel`,
        value: `${emoji} ${chx}`,
        inline: true,
    },
    {
        name:`Welcome Embed`,
        value:`${emoji} ${em}`,
        inline:true
    },
    {
        name:`Welcome Author`,
        value: `${emoji} ${author}`,
        inline:true,
    },
    {
        name:`Welcome Message`,
        value:`${emoji} \n ${welcome} `,
        inline: true,
    },
    {
        name:`Welcome Footer`,
         value: `${emoji} ${footers} `,
        inline: true,
    },
    {
        name:`Welcome Image`,
        value: `${emoji} ${image} `,
        inline: true,
    },

    { 
      name:`Welcome Thumbnail`,
      value:`${emoji} ${thumbnail} `,
      inline:true,
      
    },
    {
        name:`Welcome Color`,
        value:`${emoji} ${colors} `,
        inline: true,
    },
)
       message.reply({embeds:[stats]})
      
    } else if(args[0] === "author") {
      
      let authorembed = new MessageEmbed()
      .setDescription(`${checked} Succesfully updated Author`)
      .setColor(color)
      db.set(`author_${message.guild.id}`, args.splice(1).join(' '))
      return message.reply({embeds:[authorembed]})
      
      
    } else if(args[0] === "color") {
      
      let authorembed = new MessageEmbed()
      .setDescription(`${checked} Succesfully updated Color`)
      .setColor(color)
      db.set(`color_${message.guild.id}`, args.splice(1).join(' '))
      return message.reply({embeds:[authorembed]})
      
      
    }
      else if(args[0] === "thumbnail") {
        if(args[1] === '{guild.icon}'){
                  let x = new MessageEmbed()
        .setDescription(`${checked} Succesfully updated Thumbnail`)
        .setColor(color)
         db.set(`thumbnail_${message.guild.id}`,args[1])
        message.reply({embeds:[x]})
       
        }
        if(args[1]== '{user.icon}') {
                            let x = new MessageEmbed()
        .setDescription(`${checked} Succesfully updated Thumbnail`)
        .setColor(color)
         db.set(`thumbnail_${message.guild.id}`,args[1])
        return message.reply({embeds:[x]})
        }
        let icon = args[1]
      //  if(!icon) icon = args[0]
      let no = new MessageEmbed()
      .setDescription(`${xmark} Not a well formed URL`)
      .setColor(error)
        let x = new MessageEmbed()
        .setDescription(`${checked} Succesfully updated Thumbnail`)
        .setColor(color)
        
                if (message.attachments.first()) {
      icon = message.attachments.first().url
         console.log(icon)
      db.set(`thumbnail_${message.guild.id}`, icon || args[1])
        return message.reply({embeds:[x]})
      .catch(() => {
        message.reply({embeds:[no]})
        
      })
    } 
  
 
    }else if(args[0] == 'embed') {
      if(!args[1]) return message.reply({embeds:[{description:`${xmark} welc embed [on/off]`,color:error}]})
      if(args[1] == 'on'){
        db.set(`embedoff_${message.guild.id}`,true)
        message.reply({embeds:[{description:`${checked} Succesfully enabled embed`,color:color}]})
      }else if(args[1] == 'off'){
        db.delete(`embedoff_${message.guild.id}`)
        message.reply({embeds:[{description:`${checked} Succesfully disabled embed`,color:color}]})
      }
    }
      

  }
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
}