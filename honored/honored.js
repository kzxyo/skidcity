const Discord = require('discord.js');
const { Client, Intents, MessageEmbed } = require('discord.js');
const colors = require('colors');
const DisTube = require('distube');
const { SpotifyPlugin } = require("@distube/spotify");
const fs = require('fs');
const path = require('path');

const sessionIntents = [
  Intents.FLAGS.GUILDS,
  Intents.FLAGS.GUILD_MEMBERS,
  Intents.FLAGS.GUILD_BANS,
  Intents.FLAGS.GUILD_EMOJIS_AND_STICKERS,
  Intents.FLAGS.GUILD_INTEGRATIONS,
  Intents.FLAGS.GUILD_WEBHOOKS,
  Intents.FLAGS.GUILD_INVITES,
  Intents.FLAGS.GUILD_VOICE_STATES,
  Intents.FLAGS.GUILD_MESSAGES,
  Intents.FLAGS.GUILD_MESSAGE_REACTIONS,
  Intents.FLAGS.GUILD_MESSAGE_TYPING,
  Intents.FLAGS.DIRECT_MESSAGES,
  Intents.FLAGS.DIRECT_MESSAGE_REACTIONS,
  Intents.FLAGS.DIRECT_MESSAGE_TYPING,
];

const session = new Client({
  partials: [
    'MESSAGE',
    'CHANNEL',
    'REACTION',
    'USER',
    'GUILD_MEMBER',
    'MESSAGE',
    'USER',
    'REACTION',
    'MESSAGE',
    'CHANNEL',
    'GUILD_MEMBER',
    'VOICE',
  ],
  intents: sessionIntents
});

session.developers = require('/root/rewrite/Utils/config.json').developers;
session.token = require('/root/rewrite/Utils/config.json').token;
session.gemini = require('/root/rewrite/Utils/config.json').gemini;
session.footer = require('/root/rewrite/Utils/config.json').footer;
session.lastfmkey = require('/root/rewrite/Utils/config.json').lastfmkey;
session.invite = require('/root/rewrite/Utils/config.json').invite;
session.server = require('/root/rewrite/Utils/config.json').server;
session.color = require('/root/rewrite/Utils/config.json').color;
session.prefix = require('/root/rewrite/Utils/config.json').prefix;
session.warn = require('/root/rewrite/Utils/config.json').warn;
session.mark = require('/root/rewrite/Utils/config.json').mark;
session.green = require('/root/rewrite/Utils/config.json').green;
session.grant = require('/root/rewrite/Utils/config.json').grant;
session.next = require('/root/rewrite/Utils/config.json').next;
session.previous = require('/root/rewrite/Utils/config.json').previous;
session.skip = require('/root/rewrite/Utils/config.json').skip;
session.cancel = require('/root/rewrite/Utils/config.json').cancel;
session.genius = require('/root/rewrite/Utils/config.json').genius;
session.rival = require('/root/rewrite/Utils/config.json').rival;
session.log = require('/root/rewrite/Utils/logging.js')
session.commands = new Discord.Collection();
session.aliases = new Discord.Collection();

session.on('ready', () => {
  session.log('Connection:', `Logged in as ${session.user.username} (${session.user.id})`);
});

new SpotifyPlugin({
  parallel: true,
  emitEventsAfterFetching: false,
  api: {
    clientId: '',
    clientSecret: '',
    topTracksCountry: "VN",
  },
});

const player = new DisTube.DisTube(session, {
  searchSongs: 0,
  searchCooldown: 0,
  leaveOnEmpty: true,
  emptyCooldown: 0,
  leaveOnFinish: false,
  leaveOnStop: true,
  youtubeDL: true,
  plugins: [new SpotifyPlugin()],
});


player.on("playSong", (queue, song) => {
    const guild = queue.textChannel.guild;
    const textChannel = guild.systemChannel || guild.channels.cache.find(channel => channel.type === 'GUILD_TEXT');
    if (!textChannel) return;

    textChannel.send({
      embeds: [
        new MessageEmbed()
          .setDescription(`> :notes: Started playing: **[${song.name}](${song.url})**`)
          .setColor(session.color)
      ]
    });
  })

  .on("addSong", (queue, song) => queue.textChannel.send({
    embeds: [
      new MessageEmbed()
        .setDescription(`> :notes: **[${song.name}](${song.url})** has been added to the queue`)
        .setColor(session.color)
    ]
  }))
  .on("playList", (message, queue, playlist, song) => message.channel.send({
    embeds: [
      new MessageEmbed()
        .setDescription(`> :notes: Successfully loaded **[${playlist.name}](${playlist.url})** to the queue`)
        .setColor(session.green)
    ]
  }))
  .on("addList", (queue, playlist) => queue.textChannel.send({
    embeds: [
      new MessageEmbed()
        .setDescription(`> :notes: Loading up **[${playlist.name}](${playlist.url})**, may take a second...`)
        .setThumbnail(playlist.thumbnail)
        .setColor(session.color)
    ]
  }))
  .on("error", (channel, error) => {
    console.error(error)
    channel.send({
      embeds: [
        new MessageEmbed()
          .setColor(session.warn)
          .setDescription(`${session.mark} Something went wrong, contact support`)
      ]
    })
  })
  .on("noRelated", (queue) => {
    queue.textChannel.send({
      embeds: [
        new MessageEmbed()
          .setDescription(`${session.mark} Couldnt find that song`)
          .setColor(session.warn)
      ]
    })
  })
  .on("initQueue", (queue) => {
    queue.autoplay = false;
    queue.volume = 50;
  })
  .on("finish", async (queue) => {
    queue.textChannel.send({
      embeds: [
        new MessageEmbed()
          .setDescription(`${session.mark} The queue has ended`)
          .setColor(session.warn)
      ]
    });
  })
  .on("empty", (queue) => {
    queue.textChannel.send({
      embeds: [
        new MessageEmbed()
          .setDescription(`> I am leaving the voice channel due to inactivity`)
          .setColor(session.color)
      ]
    })
  })

session.player = player;

const logging = require('/root/rewrite/Utils/logging.js');
session.log = logging.sendConsoleMessage;

process.on('unhandledRejection', (reason, promise) => {
  session.log('Unhandled Rejection:', `Reason: ${reason}, Promise: ${promise}`);
});

session.log('Caching:', 'Caching all users...');
session.users.fetch()
  .then(users => {
    session.log('Caching:', 'All users cached successfully');
    session.log('Caching:', 'Caching all guilds...');
    session.guilds.fetch()
      .then(guilds => session.log('Caching:', 'All guilds cached successfully'))
      .catch(error => session.log('Caching:', `Error caching guilds: ${error}`));
  })
  .catch(error => session.log('Caching:', `Error caching users: ${error}`));


try {
  session.login(session.token)
    .then(() => {
      session.log("Connection:", "Successfully connected to Discord API");
    })
    .catch((err) => {
      session.log("Token Login:", `Failed to log in through the Discord API. Error details: ${err}`);
      process.exit(1);
    });
} catch (error) {
  session.log("Bot Initialization:", `Error during bot initialization: ${error}`);
  process.exit(1);
}

function loadEvents(session, eventsDir) {
  const eventFiles = fs.readdirSync(eventsDir);

  for (const file of eventFiles) {
    const filePath = path.join(eventsDir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      loadEvents(session, filePath); // Recursively call loadEvents for subdirectories
    } else if (file.endsWith('.js')) {
      try {
        const eventHandler = require(filePath);
        if (eventHandler.configuration && eventHandler.run) {
          session.on(eventHandler.configuration.eventName, (...args) => eventHandler.run(session, ...args));
          session.log("Events:", `Registered event ${eventHandler.configuration.eventName} in file ${file}`);
        } else {
          session.log("Events:", `Invalid event handler file ${file}: Missing configuration or run function`);
        }
      } catch (error) {
        session.log("Events:", `Error registering event in file ${file}: ${error.message}`);
      }
    }
  }
}

const eventsDir = '/root/rewrite/Events';
loadEvents(session, eventsDir);




function loadCommands(session) {
  const commandsDir = '/root/rewrite/Commands';
  const commandFolders = fs.readdirSync(commandsDir);

  for (const folder of commandFolders) {
    const folderPath = path.join(commandsDir, folder);
    if (fs.statSync(folderPath).isDirectory()) {
      const commandFiles = fs.readdirSync(folderPath).filter(file => file.endsWith('.js'));

      for (const file of commandFiles) {
        try {
          const commandFile = require(path.join(folderPath, file));
          if (commandFile.configuration && typeof commandFile.run === 'function') {
            session.commands.set(commandFile.configuration.commandName, commandFile);

            commandFile.configuration.aliases.forEach(alias => {
              session.aliases.set(alias, commandFile.configuration.commandName);
            });

            session.log("Commands:", `Registered command ${commandFile.configuration.commandName}`);
          } else {
            session.log("Commands:", `Invalid command file ${file}: Missing configuration or run function`);
          }
        } catch (error) {
          session.log("Commands:", `Error registering command in file ${file}: ${error.message}`);
        }
      }
    }
  }
}

loadCommands(session);
