
const{ MessageEmbed,Permissions } = require('discord.js');
const { default_prefix , color,error,owner,checked,xmark } = require("../config.json")
const db = require('quick.db')
const talkedRecently = new Set();
module.exports = {
	name: 'role',
	description: 'Just a test command',
	aliases:[],
	usage: ' \```YAML\n\n role add @heist {role} \nrole remove @heist {role} \nrole create{role_name} {emoji} \nrole delete {role_mention} \nrole icon {emoji} \nrole humans {role}\```',
  category: "moderation",
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

        let missperms = new MessageEmbed()
    .setDescription(`${xmark} You're missing \`MANAGE_ROLES\` permission`)
    .setColor(error)
   let imissperms = new MessageEmbed()
    .setDescription(`${xmark} i don't have perms`)
    .setColor(error)

     //if(message.author.id !== message.guild.ownerId) return message.channel.send({embeds:[onlyown]});

    if (!message.member.permissions.has([ Permissions.FLAGS.MANAGE_ROLES]))  return message.reply({ embeds:[missperms]});
    if (!message.guild.me.permissions.has([ Permissions.FLAGS.MANAGE_ROLES])) return message.reply({ embeds:[imissperms]});
                const trustedno = new MessageEmbed()
            .setDescription(`${xmark} Only trusted admins can use this command`)
            .setColor(error)
        let saysum = new MessageEmbed()
        .setDescription(`${xmark} You must provide a user`)
        .setColor(error)
        let saysumnn = new MessageEmbed()
        .setDescription(`${xmark} You must provide a valid role`)
        .setColor(error)
        let rolencuk = new MessageEmbed()
        .setDescription(`${xmark} Can't find that role`)
        .setColor(error)
        let higherrole = new MessageEmbed()
        .setDescription(`${xmark} That role is higher than yours`)
        .setColor(error)
        
          
 if(!args[0]){
            let example = new MessageEmbed()
            .setDescription(`<:allstarrole:997233388635312198> **Role Commands** \n <:allstar:1001031487103193108>  role  add  @heist <<role>> \n <:allstar:1001031487103193108>  role remove @heist <<role>> \n <:allstar:1001031487103193108> role create <<role_name>>  <<custom_emoji>>\n <:allstar:1001031487103193108>  role delete <<role_mention>> \n <:allstar:1001031487103193108> role humans @users \n <:allstar:1001031487103193108> role icon @role <:sensowelcoming:991027971949219920> `)
            .setColor(color)
            message.reply({embeds:[example]})
        }
        else if(args[0].toLowerCase() == "add"){
          
            let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[1]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args[1]) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args[1]) || args[1] || message.member;
            const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[2]) || message.guild.roles.cache.find(r => r.name === args.slice(2).join(' ')) || message.guild.roles.cache.find(role => role.name === args[2]) || message.guild.roles.cache.find(role => role.name.includes(args[2]))
            if (!mentionedMember) return message.channel.send({ embeds:[saysum]});
            if (!args[2]) return message.channel.send({ embeds:[saysumnn]});
            if (!role) return message.channel.send({ embeds:[rolencuk]});
            if (message.member.roles.highest.position <= role.position) return message.reply({ embeds:[higherrole]});
          
          try {
             await mentionedMember.roles.add(role.id)//.catch(err => console.log(err))
          } catch(error) {
            console.log(error)
          }

            const rolegiveEmbed = new MessageEmbed()
              .setDescription(`${checked} Updated roles for ${mentionedMember}`)
              .setColor(color)
            return message.reply({embeds:[rolegiveEmbed]})
        

        }else if(args[0].toLowerCase() == "remove"){
            let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[1]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args[1]) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args[1]) || args[1] || message.member;
            const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[2]) || message.guild.roles.cache.find(r => r.name === args.slice(2).join(' ')) || message.guild.roles.cache.find(role => role.name === args[2]) || message.guild.roles.cache.find(role => role.name.includes(args[2]))
         if (!mentionedMember) return message.channel.send({ embeds:[saysum]});
            if (!args[2]) return message.channel.send({ embeds:[saysumnn]});
            if (!role) return message.channel.send({ embeds:[rolencuk]});
                 if (message.member.roles.highest.position <= role.position) return message.reply({ embeds:[higherrole]})
          //if(message.member.roles.highest.comparePositionTo(mentionedMember.roles.highest) >= 0)  return message.reply({ embeds:[higherrole]})
            await mentionedMember.roles.remove(role.id).catch(err => console.log(err))
            const rolegiveEmbed = new MessageEmbed()
              .setDescription(`${checked} Updated roles for ${mentionedMember}`)
              .setColor(color)
            return message.reply({embeds:[rolegiveEmbed]})
         
        }else if(args[0].toLowerCase() == "create"){ 
          if(!args[2]) {
                      let icon = new MessageEmbed()
          .setDescription(`${checked} created role named ${args[1]}`)
          .setColor(color)
          let roleName = args[1];
            await message.guild.roles.create({
            name: args[1], 

                                 
        }).catch(() => { return message.reply({embeds:[imissperms]})}).then(message.reply({embeds:[icon]}));


            
          }
          else {
                      let icon = new MessageEmbed()
          .setDescription(`${checked} created role named ${args[1]}`)
          .setColor(color)
          let roleName = args[1];
       let emoji =  args[2].match(/<:.*:(.*)>/)[1]
            await message.guild.roles.create({
            name: args[1], 
            icon:emoji,
                                 
        }).catch(() => {return message.reply({embeds:[imissperms]})}).then(message.reply({embeds:[icon]}));


            
          }


        }else if(args[0].toLowerCase() == "delete"){
                  let managed = new MessageEmbed()
        .setDescription(`${xmark} That role is managed`)
        .setColor(error)
         let done = new MessageEmbed()
        .setDescription(`${checked} Succesfully deleted role`)
        .setColor(color)
          
          
          
         const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1]) || message.guild.roles.cache.find(r => r.name === args.slice(1).join(' ')) || message.guild.roles.cache.find(role => role.name === args[1]) || message.guild.roles.cache.find(role => role.name.includes(args[1]))

            if (!args[1]) return message.channel.send({ embeds:[saysumnn]});
            if (!role) return message.channel.send({ embeds:[rolencuk]});
            if (message.member.roles.highest.position <= role.position) return message.reply({ embeds:[higherrole]});
            if(role.managed) return message.reply({embeds:[managed]})
          try {
            
            await role.delete().catch(() => {/*Ignore error*/})

          } catch {}
          message.reply({embeds:[done]})
          
        }else if(args[0].toLowerCase() == "humans"){

                   let trustedusers = db.get(`trustedusers_${message.guild.id}`)
          if(trustedusers && trustedusers.find(find => find.user == message.author.id)) {
        let managed = new MessageEmbed()
        .setDescription(`<:allstarwarn:996517869791748199> That role is managed`)
        .setColor(error)
           const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1]) || message.guild.roles.cache.find(r => r.name === args.slice(1).join(' ')) || message.guild.roles.cache.find(role => role.name === args[1]) || message.guild.roles.cache.find(role => role.name.includes(args[1]))
            if (!role) return message.channel.send({ embeds:[rolencuk]});
           if(role.managed) return message.reply({embeds:[managed]})
            if (message.member.roles.highest.position <= role.position) return message.reply({ embeds:[higherrole]});
          let embed = new MessageEmbed()
          .setDescription(`<:allstarrole:997233388635312198> Role Humans \n <:allstar:1001031487103193108> roling ${message.guild.members.cache.size} humans`)
          .setColor(color)
          try {
           /* message.guild.members.fetch.map(async m => {
              
               await m.roles.add(role.id)
               console.log(m.id)
          }).then(message.reply({embeds:[embed]})) */
            //client.shard.broadcastEval(`message.guild.members.cache`)
        /*   message.guild.members.fetch().then(m => {
             let roled = 0;
                                  let embed = new MessageEmbed()
          .setDescription(`<:allstarrole:997233388635312198> Role Humans \n <:allstar:1001031487103193108> Attempting to role ${m.size} humans`)
          .setColor(color)
          message.reply({embeds:[embed]})
             for (const m of m.size) {
              m.forEach(ms => {
                if(ms.bot) return
                if(ms.roles.cache.has(role.id)) return;
                roled++
              ms.roles.add(role.id)
            })
             }
              message.reply({embeds:[new MessageEmbed().setDescription(`${checked} Succsefully roled ${roled} humans`).setColor(color)]})
             
           })
            */
           message.guild.members.fetch().then(human => {
                        let embed = new MessageEmbed()
          .setDescription(`<:allstarrole:997233388635312198> Role Humans \n <:allstar:1001031487103193108> Attempting to role ${human.size - role.members} humans`)
          .setColor(color)
              
              human.forEach(m => {
                if(m.roles.cache.has(role.id)) return;
              m.roles.add(role.id)
            })
              
            }) 
            await message.reply({embeds:[embed]}) 


            /*
          client.shard.broadcastEval(`
            message.guild.members.cache.map(async m => {
            await m.roles.add(role.id)
           }).then(message.reply({embeds:[embed]}))
           `); */
   
          } catch {}
          

          


          
          
        }else return message.reply({embeds:[trustedno]})
      

        }else if(args[0].toLowerCase() == "icon"){
        const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[1]) || message.guild.roles.cache.find(r => r.name === args.slice(1).join(' ')) || message.guild.roles.cache.find(role => role.name === args[1]) || message.guild.roles.cache.find(role => role.name.includes(args[1]))

            if (!args[1]) return message.channel.send({ embeds:[saysumnn]});
            if (!role) return message.channel.send({ embeds:[rolencuk]});
          
        let icon = new MessageEmbed()
          .setDescription(`${checked} Updated role icon`)
          .setColor(color)
       let emoji =  args[2].match(/<:.*:(.*)>/)[1]
            await message.guild.roles.edit(role,{
            icon:emoji,
                                 
        }).catch((e) => {return message.reply({embeds:[imissperms]})}).then(message.reply({embeds:[icon]}));



          
          
          
        } else {

          let mentionedMember = await message.mentions.members.first() || message.guild.members.cache.get(args[0]) || message.guild.members.cache.find(r => r.user.username.toLowerCase() === args[0]) || message.guild.members.cache.find(r => r.displayName.toLowerCase() === args[0]) || args[0] || message.member;
          const role = message.mentions.roles.first() || message.guild.roles.cache.get(args[0]) || message.guild.roles.cache.find(r => r.name === args.slice(0).join(' ')) || message.guild.roles.cache.find(role => role.name === args[0]) || message.guild.roles.cache.find(role => role.name.includes(args[0]))
     
          if (!role) return 
          if (message.member.roles.highest.position <= role.position) return message.reply({ embeds:[higherrole]});
        
          if(mentionedMember.roles.cache.has(role.id)){
                      try {
           await mentionedMember.roles.add(role.id)//.catch(err => console.log(err))
        } catch(error) {
          console.log(error)
        }
          return   message.reply({embeds:[
               {
                 description:`${checked} removed ${role.name} from ${mentionedMember.user.tag}`,
                 color:color
               }
             ]})
           }
          if(mentionedMember.roles.cache.has(role.id)){
                      try {
           await mentionedMember.roles.remove(role.id)//.catch(err => console.log(err))
        } catch(error) {
          console.log(error)
        }
               return    message.reply({embeds:[
                             {
                 description:`${checked} added ${role.name} to ${mentionedMember.user.tag}`,
                 color:color
               }
             ]})
          
      

        }
        }
      }
      
            talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }
};