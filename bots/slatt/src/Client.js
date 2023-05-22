const Discord = require('discord.js');
const {
  Intents,
} = require('discord.js');
const {
  readdir,
  readdirSync
} = require('fs');
const {
  join,
  resolve 
} = require('path');
const AsciiTable = require('ascii-table');
require('discord-reply');

class Client extends Discord.Client {
  constructor(config, options = {
    disableMentions: 'everyone',
    intents: [
      Intents.FLAGS.GUILDS,
      Intents.FLAGS.GUILD_MESSAGES,
      Intents.FLAGS.DIRECT_MESSAGES,
      Intents.FLAGS.DIRECT_MESSAGE_TYPING,
      Intents.FLAGS.GUILD_WEBHOOKS,
      Intents.FLAGS.GUILD_INTEGRATIONS,
      Intents.FLAGS.GUILD_PRESENCES,
      Intents.FLAGS.GUILD_VOICE_STATES,
      Intents.FLAGS.GUILD_INVITES,
      Intents.FLAGS.GUILD_MEMBERS,
      Intents.FLAGS.GUILD_MESSAGE_REACTIONS,
      Intents.FLAGS.DIRECT_MESSAGE_REACTIONS,
    ]
  }) {
    super(options);
    this.logger = require('./utils/logger.js');
    this.db = require('./utils/db.js');
    this.types = {
      INFO: 'info',
      FUN: 'fun',
      LASTFM: 'lastfm',
      SEARCH: 'search',
      MISC: 'misc',
      MOD: 'mod',
      SERVER: 'server',
      OWNER: 'owner'
    };
    this.commands = new Discord.Collection();
    this.aliases = new Discord.Collection();
    this.subcommands = new Discord.Collection();
    this.subcommand_aliases = new Discord.Collection();
    this.topics = [];
    this.ownerId = ["540071388069756931", "288402111916539914"];
    this.utils = require('./utils/utils.js');
    this.emotes = require('./utils/json/emojis.json')
    this.logger.info('Initializing...');
  }
  loadEvents(path) {
    readdir(path, (err, files) => {
      if (err) this.logger.error(err);
      files = files.filter(f => f.split('.').pop() === 'js');
      if (files.length === 0) return this.logger.warn('No events found');
      this.logger.info(`${files.length} event(s) found...`);
      files.forEach(f => {
        const eventName = f.substring(0, f.indexOf('.'));
        const event = require(resolve(__basedir, join(path, f)));
        super.on(eventName, event.bind(null, this));
        delete require.cache[require.resolve(resolve(__basedir, join(path, f)))]; // Clear cache
        this.logger.info(`Loading event: ${eventName}`);
      });
    });
    return this;
  }
  loadCommands(path) {
    this.logger.info('Loading commands...');
    let table = new AsciiTable('Commands');
    table.setHeading('File', 'Aliases', 'Type', 'Status');
    readdirSync(path).filter(f => !f.endsWith('.js')).forEach(dir => {
      const commands = readdirSync(resolve(__basedir, join(path, dir)))
      commands.forEach(f => {
        if (f.endsWith('.sub')) {
          const files = readdirSync(resolve(__basedir, join(path, dir, f))).filter(f => f.endsWith('js'));
          files.forEach(subcmd => {
            const Subcommand = require(resolve(__basedir, join(path, dir, f, subcmd)));
            const subcommand = new Subcommand(this);
            if (subcommand.name) {
              this.subcommands.set(subcommand.base + ' ' + subcommand.name, subcommand)
            }
            if (subcommand.aliases) {
              subcommand.aliases.forEach(a => {
                this.subcommand_aliases.set(subcommand.base + ' ' + a, subcommand)
              })
            }
          })
        } else if (f.endsWith('.js')) {
          const Command = require(resolve(__basedir, join(path, dir, f)));
          if(Command !== {}) {
          const command = new Command(this); // Instantiate the specific command
          if (command.name && !command.disabled) {
            // Map command
            this.commands.set(command.name, command);
            // Map command aliases
            let aliases = '';
            if (command.aliases) {
              command.aliases.forEach(alias => {
                this.aliases.set(alias, command);
              });
              aliases = command.aliases.join(', ');
            }
            table.addRow(f, aliases, command.type, 'pass');
          }
        } else {
          this.logger.warn(`${f} failed to load`);
          table.addRow(f, '', '', 'fail');
          return;
        }
      }
      })
    });
    this.logger.info(`\n${table.toString()}`);
    return this;
  }

  users() {
    return
  }
  unloadCommands(path) {
    let table = new AsciiTable('Commands');
    table.setHeading('File', 'Aliases', 'Type', 'Status');
    readdirSync(path).filter(f => !f.endsWith('.js')).forEach(dir => {
      const commands = readdirSync(resolve(__basedir, join(path, dir)))
      commands.forEach(f => {
        if (f.endsWith('.sub')) {
          const files = readdirSync(resolve(__basedir, join(path, dir, f))).filter(f => f.endsWith('js'));
          files.forEach(subcmd => {
            const Subcommand = require(resolve(__basedir, join(path, dir, f, subcmd)));
            const subcommand = new Subcommand(this);
            if (subcommand.name) {
              this.subcommands.delete(subcommand.base + ' ' + subcommand.name)
            }
            if (subcommand.aliases) {
              subcommand.aliases.forEach(a => {
                this.subcommand_aliases.delete(subcommand.base + ' ' + a)
              })
            }
          })
        } else if (f.endsWith('.js')) {
          const Command = require(resolve(__basedir, join(path, dir, f)));
          const command = new Command(this);
          if (command.name) {
            this.commands.delete(command.name);
            let aliases = '';
            if (command.aliases) {
              command.aliases.forEach(alias => {
                this.aliases.delete(alias);
              });
              aliases = command.aliases.join(', ');
            }
            table.addRow(f, aliases, command.type, 'pass');
          }
        } else {
          table.addRow(f, '', '', 'fail');
          return;
        }
      })
    });
    this.logger.info(`\n${table.toString()}`);
    return this;
  }
  isOwner(user) {
    if (this.ownerId.some(x => x === user.id)) return true
    else return false;
  }
}

module.exports = Client;
