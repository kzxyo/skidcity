const discord = require('discord.js');
const client = new discord.Client({ intents: discord.Intents.ALL });
const client2 = new discord.Client({ intents: discord.Intents.ALL });
const disbut = require('./src/index');
disbut(client);

client.on('ready', () => {
    console.log(client.user.tag);
});

client2.on('ready', () => console.log('2 ready'))

client.on('message', async (message) => {
    if (message.author.bot) return;
    if (message.content.startsWith('o')) {

        const embed = new discord.MessageEmbed().setDescription(`${discord.version}`);

        let option = new disbut.MessageMenuOption()
            .setLabel('op').setValue('hi').setDescription('ss');

        let reload = new disbut.MessageMenuOption().setLabel('reload').setEmoji('780988312172101682').setValue('reload');

        let select = new disbut.MessageMenu()
            .setID('hey')
            .addOptions(option, reload)
            // .setMaxValues(2)
            .setPlaceholder('opla');

        // console.log(select)

        let btn = new disbut.MessageButton()
            .setLabel(' ')
            .setID('id')
            .setStyle('blurple')
            .setDisabled();

        let group1 = new disbut.MessageActionRow().addComponent(btn);

        let group2 = new disbut.MessageActionRow().addComponent(select);

        let m = await message.channel.send('hi', { components: [group1, group2] });

        /*let collector = m.createMenuCollector((b) => b, { time: 10000 });

        collector.on('collect', (b) => {
            console.log(b.id);
            b.reply.defer();
        });

        collector.on('end', (b) => console.log('end'));*/
    }
});

client.on('clickButton', async (button) => {

    let btn = new disbut.MessageButton().setEmoji('785062885952192512').setID('d').setStyle('blurple');

    button.reply.think().then(async (r) => {
        await wait(1000);
        r.edit('awaited', btn);
    });
});

client.on('clickMenu', async (menu) => {
    // let reply = await menu.reply.think();
    if (menu.values[0] === 'reload') {
        menu.message.components[0].components[0].setDisabled(false);
        console.log(menu.message.components)
        menu.message.update('hey', { components: menu.message.components })
    }
});

client.login('');

function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
