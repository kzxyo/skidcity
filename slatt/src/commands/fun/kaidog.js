const Command = require('../Command.js');
const ReactionMenu = require('../ReactionMenu.js');
const {
    MessageEmbed
} = require('discord.js');
const art = [
    'https://cdn.discordapp.com/attachments/762122444244779019/789885986871967804/image9.jpg',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885984086163488/image8.gif',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885983797411874/image7.jpg',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885983507087360/image6.jpg',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885982966153216/image5.jpg',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885982559830096/image4.jpg',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885982274355230/image3.jpg',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885981909581914/image1.jpg',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885981636821012/image0.png',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885618297241600/image7.png',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885617814765618/image6.gif',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885616736436224/image3.jpg',
    'https://cdn.discordapp.com/attachments/762122444244779019/789885615415099462/image0.png',
    'https://cdn.discordapp.com/attachments/813455929952567306/814027434680778792/image2.jpg',
    'https://cdn.discordapp.com/attachments/813455929952567306/814027434428858388/image1.png',
    'https://cdn.discordapp.com/attachments/813455929952567306/814027434197516288/image0.png',
    'https://cdn.discordapp.com/attachments/816423520321536070/818419614576672768/image0.jpg',
    'https://cdn.discordapp.com/attachments/816423520321536070/818419614899896320/image1.jpg',
    'https://cdn.discordapp.com/attachments/816423520321536070/818419615167545405/image2.jpg',
    'https://cdn.discordapp.com/attachments/816423520321536070/818419615427198977/image3.jpg',
    'https://cdn.discordapp.com/attachments/816423520321536070/818419616070107196/image5.jpg',
    'https://cdn.discordapp.com/attachments/816423520321536070/818419617030602783/image9.jpg',
    'https://cdn.discordapp.com/attachments/816423520321536070/818419616828751882/image8.jpg',
    'https://cdn.discordapp.com/attachments/816423520321536070/818419616584957972/image7.jpg',
];
module.exports = class KaiDogCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'kaidog',
            aliases: ['uglyassdog'],
            subcommands: ['kaidog'],
            usage: 'kaidog',
            description: 't̮̟͖̥̭͉̘̄͘ḩ̖͇͙̭̫̟̋̆̆ͦe̝͍͉͖ͨ̈́ͯ́ ̵͕̼̘̖͇͙̍e̩͎͉̣̗͉̯̔͑̈͡n̗̘͍̥ͦ̌͞d̷̤̼͆ ̧̟̩̜͓ͭͣ̚ͅȉ̡̻͈̣͈̜̖͖̣̏s͍̩̥̖̻̅̕ ̠͔̙̙̺͍ͣ̇͡ć̩̹̖̣͇̥̟̯̚ö͈͕̠̙̗ͯ̎ͮ͠m͔̯̣̟̝͔̫̓͜i̴̖̳̟͓ͧͧ̉n̵̤̖͙̣̲͂ͅġ̵͎̭͔̙̳͕̘ͧ͗͐,̧͈̱̝͉̩̟͊ ͚̹̠̉͋͌͞r̺̱̟̜̦̋̍̀u̷̲̥͇̘̖̭̞̯̿͒͗ñ̟̼̖͔͇́̇̈́͜ ̷̼̹̙͓̳̲ͤr̞̮̙̘̋̆͆͡ͅuͬ̐҉̼̜͉ń̷̝̯͍̩͚͎̼͆ͫ,̸̠̭͎̙̭͓͓̲ͬ̚ ̨̫̙̣̬̩ͬ͐ͤ̃r̶̦͖͆̇u̜̫͖̲̬̬̳ͧ̈́̃̅͜n̵̝͈̟̟̪ͧͩ͗ͅ ̴̪̪͇̠͐n̴͔̭̙̹̫̲̜ͮ̏͐o̢͙̜̯͔̗̜̖̟͌ͤẅ̱̗̬̮́͘ͅ ̛̯̖ͯ̾̌y̶͍̙̜̏̄͛͐o͉͚ͩ̊̕ủ̂ͩ҉͖̻͕̮͖̲̝ͅ ͗͌͏̜̝̻͙̣n͙̥̺ͤ͞e̍ͯ͏̬͉͖̥e͈̜̮̰͇̜̘̍͘d̢̖͎̼͖ͥͤ̀ͪ ̢̫͉̥̖̫͍ͦ̎̄ͅt̵̝̙̰͔̬̮ͥ̒ͣ̓ǫ̲̻͈̤ͤ ̤̫̦̮̖̝̬̏̂͗͘r̜̘̙̪̫͈͇̟ͦ͡u̲͚̟ͮ̄͠n͔͍̱̘ͥͩ͐ͣ̕ ̝̃͝ͅy̅ͮ҉̹̹̗̠̱͈̗ǒ̵̖̫͈̙uͥ̓̚͏͚̞̤ ̀̑͏̲̬̹̦̥̟ņ͍̙̰̾ͯ͌͒e̻͔̙̬͍͑̕ë͖͙͉̹̺̰̺́̌͋́ͅd̼̞̙͎͑̀ ͙̻̳̫̟͂ͫ͘t̡͔͙̫͍̪̙ͮo̻͉͔̟̘̅̈́͠ ̘̦̣̣̲̤̀͘w͉̥̼̟̖̣̱̓ͬͪ͟a̱̱̹̪̬̺͖̼̓́k̨̻̫̞͈̲̲͈̔̉e̖̻̺̍ͩ̇͋͢ͅ ̷̞̬̻͔̯̋u̳͕̯̭̤͈͕̥͒̾͝p̤̭̱̱ͮ͗͒̇͟ ̩͇̻͉͖ͪ̀ͅŗ̘͎͇̐͛ͯ̚ǔ͚̥̺̬͚ͩ̀n͍͕̠̭͍̥͖̂ͭ͒͟ ͎̤̥̒͊̂ͧ͜y̰̬͗̌͂̕o̶͚͍̩͙̜͆u͔̘̹̜̽̊͟ ̸̪͓̤͍͉̺͇̉a̩̭̜̦̟̬͎͈ͪ̿̀ŗ͍̭̘̳̱̐e̮͇̅͊ͩ͡ ̝̮͚͔̹̟̉ͬ̕d͈̭̳͇̲̠̮̣͌̽ͭ̕r̗͖̤͚̳̪͔̓́e̻̞̙̺̺͙̖̟̎͑ͯ̚͡a̗͔̥̪̠͆͗ͧ́m̖̬̼̰̩̙͕̲͐̓͟ï̫̟͙̯͚͇̖̈́̄́n͉͓̬̝̬͎̂͟g̨͓͉̺̗͔͇̓̄͒̂ͅ ͎͓̼̉͊ͪ͞r̛̻͓̗̦̪͎̰̮̓ü̱̱̬͎̪̋ͭ͠n̢̖͚͉̒ ̖̘̦͍̹͕̔ͦ̑͡ẗ̳̥͖͎͈̗̯̼̏̚̚͠h̸̫̦̮͓ͬ̔i̡͙̦̠͗s̛̺͎͙̫̥̗̥̆̄̿ ̢͎̗ͦ̚i̵̤̼̟͑̌̚s̡̩̣̞̼̟̉̚ͅ ̤͉̑ͨ͆̂͝a̖̲̮͈ͯͮ̌͞ ̠̘̞͉̹̫̼̱́̽ͩͮ͘d̶͓̟̽r̯͙̞̖͇̙͆̉̇̀e̎̑͏̠͎̟͕̝̟̝̞ȃ҉͈͉͍ͅm̖̘̂̓̕ ̛̹̩̥̞ͮR̋̄͆͏̲̦̜̥̥̲̺U̷͉͔̲̟̱̺̅ͨN̡̳͉ͥ̔ͤ͐ ͑҉͓̩̠̮Rͬ̓͏̥̺U̴͇̥͔̩̥ͩͅN̵̺͕̫̉̿ͣ̇ ̜̫̥͍ͥ̿͆͜R̶̟͕̝͂U̡̙̟̳̱̜͊͌̓ͤN̛͎͖͎͎ͫ̅ ̙̟̌͜ͅT̛̘̠̲͎̈́̓H̢̤͕̎ͤ̑I̟̘͈̘̖͍ͥ̚͝Ŝ̷̞͓̭͚̋ͤ ̜̙̟̩̥̹̦̹́̀̅ͫ́Ǐ̟̠͢Sͫͫ͏͉̪̹̖ ̣̞̙̮̱̥ͬ̽̅͞Ȁ̸̪̥ ̷͍̙̤̻ͯ̐̐̍D̰͇̆͠Ṙ̸͚̮̻̪̠̠ͬͧͅḘ̢̭͛̔Ã̜̥̪̭̣͖͞M̷̰͈ͩ͒͗',
            type: client.types.FUN,
        });
    }
    async run(message) {
        let n = 0;
        const embed = new MessageEmbed()
            .setTitle('Ginger')
            .setDescription(`<@699617119561580565>`)
            .setImage(art[n])
            .setFooter(`ginger.`)
            .setColor(this.hex);
        const json = embed.toJSON();
        const previous = () => {
            (n <= 0) ? n = art.length - 1: n--;
            return new MessageEmbed(json).setImage(art[n]);
        };
        const next = () => {
            (n >= art.length - 1) ? n = 0: n++;
            return new MessageEmbed(json).setImage(art[n]);
        };

        const reactions = {
            'LEFT_ARROW': previous,
            'STOP': null,
            'RIGHT_ARROW': next,
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

        menu.reactions['STOP'] = menu.stop.bind(menu);

    }
};