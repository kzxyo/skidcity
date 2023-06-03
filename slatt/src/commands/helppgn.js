const {
    MessageEmbed
} = require('discord.js');
const Discord = require('discord.js');
module.exports = class helppgn {
    constructor(client, channel, member, cmd, prefix, embed, arr = null, interval = 5, reactions = {
        'LEFT_ARROW': this.previous.bind(this),
        'STOP': this.stop.bind(this),
        'RIGHT_ARROW': this.next.bind(this),
    }, timeout = 120000) {
        this.client = client;
        this.channel = channel;
        this.memberId = member.id;
        this.embed = embed;
        this.json = this.embed.toJSON();
        this.arr = arr
        this.prefix = prefix
        this.command = cmd
        this.interval = interval;
        this.current = 0;
        this.max = (this.arr) ? arr.length : null;
        this.reactions = reactions;
        this.emojis = Object.keys(this.reactions);
        this.timeout = timeout;
        const description = (this.arr) ? this.arr.slice(this.current, this.interval).join('\n') : null;
        const row = new Discord.MessageActionRow()
            .addComponents(
                new Discord.MessageButton()
                    .setLabel(`<`)
                    .setStyle(`PRIMARY`)
                    .setCustomId('LEFT_ARROW')
            )
            .addComponents(
                new Discord.MessageButton()
                    .setLabel(`☐`)
                    .setStyle(`DANGER`)
                    .setCustomId('STOP')
            )
            .addComponents(
                new Discord.MessageButton()
                    .setLabel(`>`)
                    .setStyle(`PRIMARY`)
                    .setCustomId('RIGHT_ARROW')
            )
        const first = new MessageEmbed()
            .addField(`Subcommands`, description)
            .setAuthor(`${this.client.user.username}`, this.client.user.avatarURL())
            .addField(`${this.client.emotes.search} Aliases`, this.command.aliases.map(c => `${c}`).join(', '), true)
            .addField(`${this.client.emotes.search} Usage`, `${this.prefix}${this.command.usage}`, true)
            .addField(`${this.client.emotes.mod} Permissions`, `${this.command.userPermissions ? this.command.userPermissions.join(', ') : 'None required'}`, true)
            .setTitle(this.embed.title + ' ' + this.client.utils.getRange(this.arr, this.current, this.interval))
            .setFooter(`${this.arr.length > 1 ? `${this.arr.length} subcommands ·` : ''} Category: ${this.command.type}`)
            .setDescription(this.command.description || '')
            .setColor('#303135')
        this.channel.send({ embeds: [first], components: [row] }).then(message => {
            this.message = message;
            this.createCollector();
        });
    }
    createCollector() {
        const filter = i => !i.isCommand() && i.isButton()
        const collector = this.message.createMessageComponentCollector({ filter, time: this.timeout });
        collector.on('collect', async reaction => {
          if (reaction.user.id != this.memberId) return reaction.reply({ content: `This button was not made for you.`, ephemeral: true })
          let newPage = this.reactions[reaction.customId] || this.reactions[reaction.customId];
          if (typeof newPage === 'function') newPage = newPage();
          if (newPage) await reaction.update({ embeds: [newPage] })
        });
        collector.on('end', () => {
          const end = new MessageEmbed()
            .setDescription(`<:info:828536926603837441> <@${this.memberId}> Reaction menu closed.`)
            .setColor("#78c6fe");
          this.message.edit({ embeds: [end], components: [] }).then(msg => {
            setTimeout(function () {
              msg.delete()
            }, 2000)
          })
        });
        this.collector = collector;
      }
    
    previous() {
        if (this.current === 0) return;
        this.current -= this.interval;
        if (this.current < 0) this.current = 0;
        return new MessageEmbed().addField(`Subcommands`, `${this.arr.slice(this.current, this.current + this.interval).join('\n')}`)
            .setAuthor(`${this.client.user.username}`, this.client.user.avatarURL())
            .addField(`${this.client.emotes.search} Aliases`, this.command.aliases.map(c => `${c}`).join(', '), true)
            .addField(`${this.client.emotes.search} Usage`, `${this.prefix}${this.command.usage}`, true)
            .addField(`${this.client.emotes.mod} Permissions`, `${this.command.userPermissions ? this.command.userPermissions.join(', ') : 'None required'}`, true)
            .setTitle(this.embed.title + ' ' + this.client.utils.getRange(this.arr, this.current, this.interval))
            .setFooter(`${this.arr.length > 1 ? `${this.arr.length} subcommands ·` : ''} Category: ${this.command.type}`)
            .setDescription(this.command.description || '')
            .setColor('#303135')
    }
    next() {
        const cap = this.max - (this.max % this.interval);
        if (this.current === cap || this.current + this.interval === this.max) return;
        this.current += this.interval;
        if (this.current >= this.max) this.current = cap;
        const max = (this.current + this.interval >= this.max) ? this.max : this.current + this.interval;
        return new MessageEmbed().addField(`Subcommands`, `${this.arr.slice(this.current, max).join('\n')}`)
            .setAuthor(`${this.client.user.username}`, this.client.user.avatarURL())
            .addField(`${this.client.emotes.search} Aliases`, this.command.aliases.map(c => `${c}`).join(', '), true)
            .addField(`${this.client.emotes.search} Usage`, `${this.prefix}${this.command.usage}`, true)
            .addField(`${this.client.emotes.mod} Permissions`, `${this.command.userPermissions ? this.command.userPermissions.join(', ') : 'None required'}`, true)
            .setTitle(this.embed.title + ' ' + this.client.utils.getRange(this.arr, this.current, this.interval))
            .setFooter(`${this.arr.length > 1 ? `${this.arr.length} subcommands ·` : ''} Category: ${this.command.type}`)
            .setDescription(this.command.description || '')
            .setColor('#303135')
    }
    stop() {
        this.collector.stop();

    }
};