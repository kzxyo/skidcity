const {
  MessageEmbed,
  MessageActionRow,
  MessageButton,
  ActionRowBuilder,
  ModalBuilder,
  TextInputBuilder,
  TextInputStyle,
  MessageSelectMenu

} = require("discord.js");
let utility = []
let security = []
let moderation = []
let confis = []
let image = []
let information = []
let games = []

const db = require('quick.db')
//const paginationEmbed = require('../paginator.js');
const fs = require("fs");
const {
  default_prefix,
  color,
  error,
  owner,
  xmark,
  reskin
} = require("../config.json");
const talkedRecently = new Set();
module.exports = {
  name: "help",
  description: "\u200B",
  aliases: ['hilfe'],
  usage: "``` help [commandName] ``` ",
  guildOnly: false,
  args: false,
  permissions: {
    bot: [],
    user: [],
  },
  execute: async (message, args, client) => {
    if (talkedRecently.has(message.author.id)) {
      message.react(`⌛`);
    } else {
      try {
        //description
        let emojis = `<:allstarreply:1001104889432256552>`;
        let prefix = db.get(`prefix_${message.guild.id}`);
        if (prefix === null) prefix = default_prefix;
         utility = []
         security = []
         moderation = []
         confis = []
         image = []
         information = []
         games = []
         await client.commands.map(cmd => {
          if(cmd.category === 'utility'){
            utility.push(`[${cmd.name}]`)
          }
          else if(cmd.category === 'security'){
            
            security.push(`[${cmd.name}]`)
          }
          else if(cmd.category === 'moderation'){
            moderation.push(`[${cmd.name}]`)
          }
          else if(cmd.category === 'image'){
            image.push(`[${cmd.name}]`)
          }
          else if(cmd.category === 'information'){
            information.push(`[${cmd.name}]`)
          }
          else if(cmd.category === 'config'){
            confis.push(`[${cmd.name}]`)
          }
          else if(cmd.category === 'games'){
            games.push(`[${cmd.name}]`)
          }

         })


        const paginationEmbed = async (
          msg,
          pages,
          buttonList,
          timeout = 15
        ) => {
          let timedout = new MessageEmbed()
            .setDescription(
              `<:allstarwarn:996517869791748199> Command Timed out`
            )
            .setColor(error);
          if (!msg && !msg.channel)
            throw new Error("Channel is inaccessible.");
          if (!pages) throw new Error("Pages are not given.");
          if (!buttonList) throw new Error("Buttons are not given.");
          if (
            buttonList[0].style === "LINK" ||
            buttonList[1].style === "LINK"
          )
            throw new Error(
              "Link buttons are not supported with discordjs-button-pagination"
            );
          if (buttonList.length !== 3) throw new Error("Need two buttons.");

          let page = 0;
          let invite = new MessageButton()
            .setLabel("Invite")
            .setURL(
              "https://discord.com/api/oauth2/authorize?client_id=938863295543251024&permissions=8&scope=bot%20applications.commands"
            )
            .setStyle("LINK");
          const row = new MessageActionRow().addComponents(
            buttonList,
            invite
          );
          const curPage = await msg.channel.send({
            embeds: [
              pages[page].setFooter({
                text: `Help Page (${page + 1} / ${pages.length})`,
                iconURL: `https://images-ext-2.discordapp.net/external/iRVLCgJyD06wlCD1m_VtVulIoSIheIr68604k4iAD8g/https/cdn.discordapp.com/emojis/1010895673794760725.png`,
              }),
            ],
            components: [row],
          });

          const filter = (i) =>
            i.customId === buttonList[0].customId ||
            i.customId === buttonList[1].customId ||
            i.customId === buttonList[2].customId;

          const collector = await curPage.createMessageComponentCollector({
            filter,
            // filter: (i) => i.user.id === message.author.id,
            time: timeout,
          });

          collector.on("collect", async (i) => {
            //console.log(i.user.id)
            if (i.user.id !== msg.author.id) return i.reply({ embeds: [new MessageEmbed().setDescription(`${xmark} You are not the author`).setColor(error)], ephemeral: true })
            switch (i.customId) {
              case buttonList[0].customId:
                page = page > 0 ? --page : pages.length - 1;
                break;
              case buttonList[1].customId:
                curPage.delete();
                break;
              case buttonList[2].customId:
                page = page + 1 < pages.length ? ++page : 0;
                break;
              default:
                break;
            }
            await i.deferUpdate();
            await i
              .editReply({
                embeds: [
                  pages[page].setFooter({
                    text: `Help Page (${page + 1} / ${pages.length})`,
                    iconURL: `https://images-ext-2.discordapp.net/external/iRVLCgJyD06wlCD1m_VtVulIoSIheIr68604k4iAD8g/https/cdn.discordapp.com/emojis/1010895673794760725.png`,
                  }),
                ],
                components: [row],
              })
              .catch(() => { });
            collector.resetTimer();
          });

          collector.on("end", () => {
            if (!curPage.deleted) {
              const disabledRow = new MessageActionRow().addComponents(
                buttonList[0].setDisabled(true),
                buttonList[1].setDisabled(true),
                buttonList[2].setDisabled(true)
              );
              curPage.edit({
                embeds: [
                  pages[page].setFooter({
                    text: `Help Page (${page + 1} / ${pages.length})`,
                    iconURL: `https://images-ext-2.discordapp.net/external/iRVLCgJyD06wlCD1m_VtVulIoSIheIr68604k4iAD8g/https/cdn.discordapp.com/emojis/1010895673794760725.png`,
                  }),
                ],
                components: [disabledRow],
              });
            }
          });

          return curPage;
        };

        let pingemoji = `<:allstarconnection:996699189432025180>`;
        let emoji = `<:allstar:1001031487103193108> `;
        if (client.ws.ping < 100) {
          let pingemoji = `<:allstarconnection:996699189432025180>`;
        } else pingemoji = `<:allstarbadconnection:996700696671948901> `;

        let embed1 = new MessageEmbed()
          .setAuthor({ name: `Allstar Help Menu `, iconURL: `${client.user.displayAvatarURL({ dynamic: true })}` })
          .setDescription('```RUBY\n\n  help + [module/command] ```')
          .addFields(
            {
              name: `Modules`,
              value: `${emoji} <:Modbadge:1010885860801126461> \`security \`,\n${emoji} <:Wave:1010885882678620193> \`welcomer \`, \n${emoji} <a:staff_shine:1010885887997001829>  \`moderation\`, \n${emoji} <:Announcements:1032194423804670004>  \`information\`, \n${emoji} <:Serverinsights:1010885871119106058>  \`utility\`, \n${emoji} <:Settings:1010885871773433866> \`config\`, \n${emoji} <:lastfm2:1042492189600657508>  \`Last.fm\`,`,
              inline: true,
            },
            {
              name: `Bot Stats`,
              value: `${emoji} ${pingemoji} \`${Math.round(client.ws.ping)
                }ms\` \n${emoji} <:dbot_icon_slash1:1032350073679511602> Commands \`${client.commands.size
                }\` \n${emoji} prefix \`${prefix} \` \n ${emoji} shard ID \`${message.guild.shardId
                }\`\n${emoji} <:allstarlink:1032192248189820998> [Support](https://discord.gg/heist)`,
              inline: true,
            },
 

          )
          .setThumbnail(`https://images-ext-2.discordapp.net/external/CG8skQzBxQFXEOaiAmi4MrpGn_euVAvCcnPvEOO6fqM/https/cdn.discordapp.com/emojis/991027971949219920.png`)

          .setFooter({
            text: `help + [module]`,
            iconURL: `https://images-ext-2.discordapp.net/external/iRVLCgJyD06wlCD1m_VtVulIoSIheIr68604k4iAD8g/https/cdn.discordapp.com/emojis/1010895673794760725.png`,
          })
          .setColor(color);

        let embed2 = new MessageEmbed()


          .addFields({
            name: `<a:staff_shine:1033522274151702640> Moderation commands [${moderation.length}]`,
            value:'\```toml\n' + `${moderation.join(", ")}` + '\```',
          //    " ```yaml\n\nkick, ban, lock, unlock, unban, mute, role*, inrole, autorole, unbanall, nuke, botclear, purge, purgeuser, nickname   ``` ",
            inline: true,
          })
          .setColor(color);

        let embedanti = new MessageEmbed()

          .addFields({
            name: `<:Modbadge:1010885860801126461> Security commands [${security.length}]`,
            value:'\```toml\n' + `${security.join(", ")}` + '\```',
         //     " ```yaml\n\nwhitelist, blacklist, antinuke*, antinuke settings, antivanity*, antibot*, antialt*, antispam* , joinlock*    ``` ",
            inline: true,
          })
          .setColor(color);
        // .setFooter({text: message.author.tag ,iconURL: client.user.displayAvatarURL()})

        let embed3 = new MessageEmbed()

          .addFields({
            name: `<:Serverinsights:1010885871119106058>  Utility commands [${utility.length}]`,
            value:'\```toml\n' + `${utility.join(", ")}` + '\```',
           //   " ```yaml\n\navatar, advice, banner, servericon, serveravatar serverbanner, steal, seticon, setbanner, image, rank, reverseavatar, emojify,  enlarge, lyrics, poll, createembed, crypto, tiktok, firstmsg, messages, leadboard, snipe, steam, editsnipe, vanityjoins, hex, spotify, urban, 8ball, screenshot, tags ``` ",
            inline: true,
          })
          .setColor(color);

        let embedwelc = new MessageEmbed()

          .addFields({
            name: `<:Wave:1010885882678620193> Welcomer commands [9]`,
            value:
              " ```toml\n[welcome channel], [welcome embed], [welcome  author], [welcome message], [welcome footer], [welcome image], [welcome variables], [welcome stats], [welcome clear]  ``` ",
            inline: true,
          }
          )
          .setColor(color);
        let embedbye = new MessageEmbed()

          .addFields(
            {
              name: `<:Wave:1010885882678620193> Goodbye commands [9]`,
              value:
                " ```toml\n[goodbye channel], [goodbye embed], [goodbye author], [goodbye message], [goodbye footer], [goodbye image], [goodbye variables], [goodbye stats], [goodbye clear]    ``` ",
              inline: true,
            })
          .setColor(color);
        let embedjoindm = new MessageEmbed()

          .addFields(
            {
              name: `<:Wave:1010885882678620193> Joindm commands [8]`,
              value:
                " ```toml\n[joindm embed], [joindm author], [joindm message], [joindm footer], [joindm image], [joindm variables], [joindm stats], [joindm clear]    ``` ",
              inline: true,
            }
          )
          .setColor(color);

        let embedinfo = new MessageEmbed()

          .addFields({
            name: `<:allstarinfo:997234551568994324> Information commands [${information.length}]`,
            value:'\```toml\n' + `${information.join(", ")}` + '\```',
           //   " ```yaml\n\nserverinfo ,whois ,perms, roleinfo, membercount, role-list, channelinfo, emoteinfo, emoji-list, boostercount, server, ping,  ``` ",
            inline: true,
          })
          .setColor(color);

        let config = new MessageEmbed()

          .addFields({
            name: `<:Settings:1010885871773433866>  Configurable commands [${confis.length}]`,
            value:'\```toml\n' + `${confis.join(", ")}` + '\```',
           //   " ```yaml\n\nprefix set, prefix delete, selfprefix set, selfprefix delete, autosnipe*, afk, boost*, xp [on/off] ``` ",
            inline: true,
          })
          .setColor(color);
        let images = new MessageEmbed()
          .setThumbnail(
            "https://media.discordapp.net/attachments/952942524085977121/1008802945980178473/IconPictures.png"
          )
          .addFields({
            name: `<:allstarutility:996512771892060160> Image commands [${image.length}]`,
            value:'\```toml\n' + `${image.join(", ")}` + '\```',
            //  " ```yaml\n\n blurple, gay, drake, ps4, meme, shit, supreme, thanos, trigger, wasted, wanted, delete  ``` ",
            inline: true,
          })
          .setColor(color);
          let gamesss = new MessageEmbed()
    
          .addFields({
            name: `<:Emoji:1032349517972000788>  Games commands [${games.length}]`,
            value:'\```toml\n' + `${games.join(", ")}` + '\```',
            //  " ```yaml\n\n blurple, gay, drake, ps4, meme, shit, supreme, thanos, trigger, wasted, wanted, delete  ``` ",
            inline: true,
          })
          .setColor(color);
        let timedout = new MessageEmbed()
          .setDescription(
            `<:allstarwarn:996517869791748199> Command Timed out`
          )
          .setColor(error);

        let invite = new MessageButton()
          .setLabel("Invite Me!")
          .setURL(
            "https://discord.com/api/oauth2/authorize?client_id=938863295543251024&permissions=8&scope=bot%20applications.commands"
          )
          .setStyle("LINK");
        if (args[0] === "security") {
          return message.reply({ embeds: [embedanti] });
        } else if (args[0] === "welcomer") {
          return message.reply({ embeds: [embedwelc] });
        } else if (args[0] === "moderation") {
          return message.reply({ embeds: [embed2] });
        } else if (args[0] === "information") {
          return message.reply({ embeds: [embedinfo] });
        } else if (args[0] === "utility") {
          return message.reply({ embeds: [embed3] });
        } else if (args[0] === "config") {
          return message.reply({ embeds: [config] });
        } else if (args[0] === "lastfm") {
          return message.reply({ embeds: [lastfm] });
        }
        let command = args[0];
        if (client.commands.has(command)) {
          command = client.commands.get(command);
          let info = ` ***${command.name} *** \n${command.description
            }\n Usage ${command.usage}\n Aliases  ${command.aliases.join(
              ", "
            )} \n ${command.aliases} `;
          let x = new MessageEmbed().setDescription(info).setColor(color);

          return message.reply({ embeds: [x] });
        }
        const button1 = new MessageButton()
          .setCustomId("previousbtn")
          .setEmoji("<a:left:1033526539188449310>")
          .setStyle("PRIMARY");

        const button2 = new MessageButton()
          .setCustomId("nextbtn")
          .setEmoji("<:right:1033526800401317928>")
          .setStyle("PRIMARY");
        const button3 = new MessageButton()
          .setCustomId("fastp")
          //.setEmoji("<:cancel:1042487068850401310> ")
          .setEmoji("<:DW_X_Mark:1032345318127304806>")
          .setStyle("DANGER");




        let pages = [
          embed1,
          embedanti,
          embedwelc,
          embedbye,
          embedjoindm,
          embed2,
          embedinfo,
          embed3,
          config,
          images,
          gamesss


        ];
        let buttonList = [button1, button3, button2];

        const timeout = "47000";
        paginationEmbed(message, pages, buttonList, timeout);


      } catch (error) {
        console.log(error);
      }
    }

    talkedRecently.add(message.author.id);
    setTimeout(() => {
      // Removes the user from the set after a minute
      talkedRecently.delete(message.author.id);
    }, 3500);
  },
};
