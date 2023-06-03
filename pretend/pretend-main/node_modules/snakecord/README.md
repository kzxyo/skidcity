# Snakecord

You've heard of the famous Snake game, right? Well, this npm/yarn package allows you to create your own CUSTOM Snake games, directly inside Discord via Discord bots!

## Installation

```bash
npm install snakecord
# or
yarn add snakecord
```

## Features
- Easy to use
- Clean and focused
- Actively maintained

## Example
```js
const SnakeGame = require('snakecord');
const Discord = require('discord.js');
const client = new Discord.Client(); // remember to add the intents that you need

const snakeGame = new SnakeGame({
    title: 'Snake Game',
    color: 'GREEN',
    timestamp: false,
    gameOverTitle: 'Game Over'
});

const config = {
    token: 'TOKEN',
    prefix: 't!'
}

client.on('ready', () => {
    console.log('Ready!');
    client.user.setActivity(`${config.prefix}help`);
});

client.on('message', async message => {
    if(!message.content.startsWith(config.prefix) || message.author.bot) {
        return;
    }

    const args = message.content.slice(config.prefix.length).trim().split(/ +/);
    const command = args.shift().toLowerCase();

    if(command === 'test') {
        return message.channel.send('Test command works.');
    } else if(command === 'snake' || command === 'snakegame') {
        return await snakeGame.newGame(message);
    } else if(command === 'help' || command === 'h') {
        const embed = new Discord.MessageEmbed()
            .setTitle('Help Menu')
            .addFields(
                { name: 'test', value: 'Check the command handler', inline: true },
                { name: 'snake', value: 'Play the snake game', inline: true },
                { name: 'help', value: 'Show this list', inline: true }
            )
            .setColor('RANDOM')
            .setTimestamp();

        return message.channel.send({ embeds: [embed] });
    }
});

client.login(config.token);
```

## In Action
![1](/images/1.PNG)

![2](/images/2.PNG)

## To-Do
- Optimizations and more optimizations
- Rewrite the whole thing in TypeScript
- Add JSDocs for easier development
- Add more features (including but not limited to)
    - Board size customizations
    - Server highscore tracking/leaderboards
    - Color customizations

## Authors
* **[Terrarian](https://github.com/Terra-rian/snakecord)** - *Current maintainer*
* **[1GPEX](https://github.com/1GPEX)** - *Original idea*
* **[Science Spot](https://github.com/Scientific-Guy)** - *Making the options*