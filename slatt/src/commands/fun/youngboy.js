const Command = require('../Command.js');
const ReactionMenu = require('../ReactionMenu.js');
const {
    MessageEmbed
} = require('discord.js');

module.exports = class youngboy extends Command {
    constructor(client) {
        super(client, {
            name: 'youngboy',
            aliases: ['yb', 'inspiration'],
            usage: 'youngboy',
            description: 'When my Discord Server get Active, all my Homies finna get admin. :100:',
            type: client.types.FUN,
        });
    }
    async run(message) {
        const art = [
            'https://cdn.discordapp.com/attachments/799642515300286514/866464146944819251/image0-20.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464147717226547/image0-13.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464148028260362/image0-1.jpg',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464148028260362/image0-1.jpg',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464148329463818/image0-11.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464189227991050/image0-10.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464189577166858/image0-9.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464189903929414/image0-8.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464190242488320/image0-7.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464190712381440/image0-6.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464191048187904/image0-5.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464191552684042/image0-4.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464191816532018/image0-3.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464192126386216/image1.png',
            'https://cdn.discordapp.com/attachments/799642515300286514/866464220408709130/image0-2.png',
            'https://cdn.discordapp.com/attachments/864774133219852318/866464903405502484/image0-17.png',
            'https://cdn.discordapp.com/attachments/866828620004982834/867233075716292618/image0-16.png'
        ];
        let n = 0;
        const embed = new MessageEmbed()
            .setTitle('Stay safe.')
            .setImage(art[n])
            .setFooter(`inspiration ${n + 1}/${art.length}`)
            .setColor(this.hex);
        const json = embed.toJSON();
        const previous = () => {
            (n <= 0) ? n = art.length - 1 : n--;
            return new MessageEmbed(json).setImage(art[n]).setFooter(`inspiration ${n + 1}/${art.length}`)

        };
        const next = () => {
            (n >= art.length - 1) ? n = 0 : n++;
            return new MessageEmbed(json).setImage(art[n]).setFooter(`inspiration ${n + 1}/${art.length}`)
        };

        const reactions = {
            '◀️': previous,
            '⏹️': null,
            '▶️': next,
        };

        const menu = new ReactionMenu(
            message.client,
            message.channel,
            message.member,
            embed,
            null,
            null,
            reactions,
            180000
        );

        menu.reactions['⏹️'] = menu.stop.bind(menu);

    }
};