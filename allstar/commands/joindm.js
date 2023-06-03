
const{ MessageEmbed,MessageActionRow,MessageButton,Permissions } = require('discord.js');
const db = require('quick.db')
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const request = require('request')
const talkedRecently = new Set();
module.exports = {
	name: 'joindm',
	description: 'jdms new users when they join',
	aliases:[],
	usage: ' \```YAML\n\n joindm embed [on/off] joindm message {text} \n joindm footer {text} \n joindm author {text} \n joindm image {image} \n joindm removeimage \n joindm clear \n joindm stats \n joindm variables \n joindm color {color} \``` ',
	category: "joindm",
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
      .setDescription(`\<a:allstarwelcome:996512695480238182>  **joindm setup** \n <:allstar:1001031487103193108> joindm embed <:allstar:1001031487103193108> joindm message \n <:allstar:1001031487103193108> joindm footer \n <:allstar:1001031487103193108> joindm author \n <:allstar:1001031487103193108> joindm image \n <:allstar:1001031487103193108> joindm removeimage \n <:allstar:1001031487103193108> joindm clear \n <:allstar:1001031487103193108> joindm stats \n <:allstar:1001031487103193108> joindm variables \n <:allstar:1001031487103193108> joindm color`)
      .setColor(color)

    if (!args[0]) {
      message.reply({embeds:[embed]})
    } 
    if (args[0] === 'message') {
      db.set(`joindmmessage_${message.guild.id}`, args.splice(1).join(' '))
      let wlcmsg = db.get(`joindmmessage_${message.guild.id}`)
      if (wlcmsg === null) {
        const setmsgembed = new MessageEmbed()
          .setDescription(`${xmark} There is no joindm message set one with ${prefix}welcome message`)
          .setColor(error)
        return message.reply({embeds:[setmsgembed]})
      } else {
        const setembed = new MessageEmbed()
          .setTitle(`${checked} joindm message updated`)
          .setDescription(`${wlcmsg}`)
          .setColor(color)
        return message.reply({embeds:[setembed]})
      }
    } else if (args[0] === 'test') {
      

      let welcome = db.get(`joindmmessage_${message.guild.id}`);
      if (welcome === null) {
                const setmsgembed = new MessageEmbed()
          .setDescription(`${xmark} There is no joindm message set one with ${prefix}welcome message`)
          .setColor(error)
        return message.reply({embeds:[setmsgembed]})
      }
      let footer = db.get(`joindmwelcembed_${message.guild.id}`);
      if (footer === null) { footer = `` }
      let image = db.get(`joindmimage_${message.guild.id}`)
      if (image === null) {
        //image = `https://cdn.discordapp.com/attachments/989999587890712606/990905254138765362/Screenshot_7.png`
      } 
      let author = db.get(`joindmauthor_${message.guild.id}`)
      if (author === null) {
        author = ""
      }
       let colors = db.get(`joindmcolor_${message.guild.id}`) 
       if(colors === null) {
         colors = color;
       }
      let thumbnail = db.get(`joindmthumbnail_${message.guild.id}`)
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
      .setDescription(`${checked} Tested joindm` )
      .setColor(color)
      console.log(thumbnail)
           const row = new MessageActionRow()
        .addComponents(
         new MessageButton()
         	.setCustomId('primary')
	        .setLabel('Message sent from Server: ' + message.guild.name)
	        .setStyle('SECONDARY')
	        .setDisabled(true)
        )
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
      let em = db.get(`joindmembed_${message.guild.id}`)
      if(em) {
        
      
      return message.author.send({content:`${message.author}`,embeds:[welcembed],components:[row]}).catch((error) =>{return message.reply(error)}).then(() => message.channel.send({embeds:[tested]}))
      } else  {
        return message.author.send({content:`${welcome}`,components:[row]}).then(() => message.channel.send({embeds:[tested]}))
      }
        
    } else if (args[0] === 'variables') {
      const member = message.author
      const ordinal = (message.guild.memberCount.toString().endsWith(1) && !message.guild.memberCount.toString().endsWith(11)) ? 'st' : (message.guild.memberCount.toString().endsWith(2) && !message.guild.memberCount.toString().endsWith(12)) ? 'nd' : (message.guild.memberCount.toString().endsWith(3) && !message.guild.memberCount.toString().endsWith(13)) ? 'rd' : 'th';
      const variablesembed = new MessageEmbed()
        .setTitle(`joindm variables`)
        .setDescription(`> {user}  - <@` + member + `>\n> {user.name}  - ` + message.author.username + `\n> {user.tag}  - ` + message.author.tag + `\n> {user.id}  - ` + message.author.id + `\n> {guild.name}  - ` + message.member.guild.name + `\n> {guild.id}  - ` + message.member.guild.id + `\n> {membercount}  - ` + message.member.guild.memberCount + `\n> {membercount.ordinal}  - ` + message.member.guild.memberCount + ordinal + `\n **Image Variables**  \n> {guild.icon}\n {user.icon}`)
        .setColor(color)
      message.reply({embeds:[variablesembed]})
    }  else if (args[0] === "clear") {
      let deleted = new MessageEmbed()
      .setDescription(`${checked} cleared joindm setup from the database`)
      .setColor(color)
      db.delete(`joindmwelcembed_${message.guild.id}`);
      db.delete(`welmessage_${message.guild.id}`)
      db.delete(`joindmimage_${message.guild.id}`)
      db.delete(`joindmauthor_${message.guild.id}`)
      db.delete(`joindmcolor_${message.guild.id}`)
      db.delete(`joindmthumbnail_${message.guild.id}`)
      return await message.reply({embeds:[deleted]})
    }
    else if(args[0] === "footer"){
      db.set(`joindmwelcembed_${message.guild.id}`, args.splice(1).join(' '))
        let footers = db.get(`joindmwelcembed_${message.guild.id}`);
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
         db.set(`joindmimage_${message.guild.id}`,args[1])
        message.reply({embeds:[x]})
       
        }
        else if(args[1]== '{user.icon}') {
                            let x = new MessageEmbed()
        .setDescription(`${checked} Succesfully updated Image`)
        .setColor(color)
         db.set(`joindmimage_${message.guild.id}`,args[1])
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
      db.set(`joindmimage_${message.guild.id}`, icon || args[1])
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

            db.delete(`joindmimage_${message.guild.id}`)
      return await message.reply({embeds:[x]})
 
    } else if(args[0] === "stats") {
  
      let footers = db.get(`joindmwelcembed_${message.guild.id}`);
      if (footers === null) footers = 'Not Set';
      
      let welcome = db.get(`joindmmessage_${message.guild.id}`)
      if (welcome === null)   welcome = 'Not Set'
      
      
      let image = db.get(`joindmimage_${message.guild.id}`)
      if(image) image = `[Image](${image})` 
      else if (image === null) image = 'Not Set'
      let author = db.get(`joindmauthor_${message.guild.id}`)
      if (author === null) {
        author = "Not Set"
      }
      let colors = db.get(`joindmcolor_${message.guild.id}`)
      if (colors === null) colors = "Not Set"
            let thumbnail = db.get(`joindmthumbnail_${message.guild.id}`)
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
      .setDescription(`<a:allstarwelcome:996512695480238182> ${message.guild.name} Joindm Stats `)
      .setColor(color)
            .addFields(
    {
        name:`Joindm Embed`,
        value:`${emoji} ${em}`,
        inline:true
    },
    {
        name:`Joindm Author`,
        value: `${emoji} ${author}`,
        inline:true,
    },
    {
        name:`Joindm Message`,
        value:`${emoji} \n ${welcome} `,
        inline: true,
    },
    {
        name:`Joindm Footer`,
         value: `${emoji} ${footers} `,
        inline: true,
    },
    {
        name:`Joindm Image`,
        value: `${emoji} ${image} `,
        inline: true,
    },

    { 
      name:`Joindm Thumbnail`,
      value:`${emoji} ${thumbnail} `,
      inline:true,
      
    },
    {
        name:`Joindm Color`,
        value:`${emoji} ${colors} `,
        inline: true,
    },
)
       message.reply({embeds:[stats]})
      
    } else if(args[0] === "author") {
      
      let authorembed = new MessageEmbed()
      .setDescription(`${checked} Succesfully updated Author`)
      .setColor(color)
      db.set(`joindmauthor_${message.guild.id}`, args.splice(1).join(' '))
      return message.reply({embeds:[authorembed]})
      
      
    } else if(args[0] === "color") {
      
      let authorembed = new MessageEmbed()
      .setDescription(`${checked} Succesfully updated Color`)
      .setColor(color)
      db.set(`joindmcolor_${message.guild.id}`, args.splice(1).join(' '))
      return message.reply({embeds:[authorembed]})
      
      
    }
      else if(args[0] === "thumbnail") {
        if(args[1] === '{guild.icon}'){
                  let x = new MessageEmbed()
        .setDescription(`${checked} Succesfully updated Thumbnail`)
        .setColor(color)
         db.set(`joindmthumbnail_${message.guild.id}`,args[1])
        message.reply({embeds:[x]})
       
        }
        if(args[1]== '{user.icon}') {
                            let x = new MessageEmbed()
        .setDescription(`${checked} Succesfully updated Thumbnail`)
        .setColor(color)
         db.set(`joindmthumbnail_${message.guild.id}`,args[1])
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
      db.set(`joindmthumbnail_${message.guild.id}`, icon || args[1])
        return message.reply({embeds:[x]})
      .catch(() => {
        message.reply({embeds:[no]})
        
      })
    } 
  
 
    }else if(args[0] == 'embed') {
      if(!args[1]) return message.reply({embeds:[{description:`${xmark} joindm embed [on/off]`,color:error}]})
      if(args[1] == 'on'){
        db.set(`joindmembedoff_${message.guild.id}`,true)
        message.reply({embeds:[{description:`${checked} Succesfully enabled embed`,color:color}]})
      }else if(args[1] == 'off'){
        db.delete(`joindmembedoff_${message.guild.id}`)
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