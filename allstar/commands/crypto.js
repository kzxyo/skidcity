
const{ MessageEmbed } = require('discord.js');
let axios = require('axios')
const { default_prefix ,color,error,owner } = require("../config.json")
const talkedRecently = new Set();
module.exports = {
	name: 'crypto',
	description: 'check any crypto currencys value',
	aliases:[],
	usage: '\```crypto btc \```',
  category: "utility",
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
            let etherium = ['eth','ethereium']
            let bitcoin = ['bitcoin','btc']
      
      
      
       if(bitcoin.includes(args[0])){
              axios.get('https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN%27%27')
        .then(response => message.reply({embeds:[new MessageEmbed().setDescription(`**Bitcoin Value** \n 1 Bitcion equals to`).addFields({name:`EUR`,value:`${response.data.EUR}`},{name:`USD`,value:`${response.data.USD}`}).setColor(color)]}))
      }
      else if(etherium.includes(args[0])){
              axios.get('https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN%27%27')
        .then(response => message.reply({embeds:[new MessageEmbed().setDescription(`**Etherium Value** \n 1 Ethereium equals to`).addFields({name:`EUR`,value:`${response.data.EUR}`},{name:`USD`,value:`${response.data.USD}`}).setColor(color)]}))
      }
      else if(args[0] === 'usdt'){
              axios.get('https://min-api.cryptocompare.com/data/price?fsym=USDT&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN%27%27')
        .then(response => message.reply({embeds:[new MessageEmbed().setDescription(`**Tether Value** \n 1 Tether equals to`).addFields({name:`EUR`,value:`${response.data.EUR}`},{name:`USD`,value:`${response.data.USD}`}).setColor(color)]}))
      }

            else if(args[0] === 'usdc'){
              axios.get('https://min-api.cryptocompare.com/data/price?fsym=USDC&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN%27%27')
        .then(response => message.reply({embeds:[new MessageEmbed().setDescription(`**USD Coin Value** \n 1 USD Coin equals to`).addFields({name:`EUR`,value:`${response.data.EUR}`},{name:`USD`,value:`${response.data.USD}`}).setColor(color)]}))
      }
            else if(args[0] === 'bnb'){
              axios.get('https://min-api.cryptocompare.com/data/price?fsym=BNB&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN%27%27')
        .then(response => message.reply({embeds:[new MessageEmbed().setDescription(`**BNB Coin Value** \n 1 BNB Coin equals to`).addFields({name:`EUR`,value:`${response.data.EUR}`},{name:`USD`,value:`${response.data.USD}`}).setColor(color)]}))
      }
            else if(args[0] === 'xrp'){
              axios.get('https://min-api.cryptocompare.com/data/price?fsym=XRP&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN%27%27')
        .then(response =>  message.reply({embeds:[new MessageEmbed().setDescription(`**XRP Coin Value** \n 1 XRP Coin equals to`).addFields({name:`EUR`,value:`${response.data.EUR}`},{name:`USD`,value:`${response.data.USD}`}).setColor(color)]}))
      }
            else if(args[0] === 'busd'){
              axios.get('https://min-api.cryptocompare.com/data/price?fsym=BUSD&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN%27%27')
        .then(response => message.reply({embeds:[new MessageEmbed().setDescription(`**Binance USD Value** \n 1 Binance USD equals to`).addFields({name:`EUR`,value:`${response.data.EUR}`},{name:`USD`,value:`${response.data.USD}`}).setColor(color)]}))
      }
            else if(args[0] === 'ada'){
              axios.get('https://min-api.cryptocompare.com/data/price?fsym=ADA&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN%27%27')
        .then(response => message.reply({embeds:[new MessageEmbed().setDescription(`**Cardano Value** \n 1 Cardano equals to`).addFields({name:`EUR`,value:`${response.data.EUR}`},{name:`USD`,value:`${response.data.USD}`}).setColor(color)]}))
      }
            else if(args[0] === 'sol'){
              axios.get('https://min-api.cryptocompare.com/data/price?fsym=SOL&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN%27%27')
        .then(response =>  message.reply({embeds:[new MessageEmbed().setDescription(`**Solana Value** \n 1 Solana equals to`).addFields({name:`EUR`,value:`${response.data.EUR}`},{name:`USD`,value:`${response.data.USD}`}).setColor(color)]}))
      }
            else if(args[0] === 'dogecoin'){
              axios.get('https://min-api.cryptocompare.com/data/price?fsym=DOGE&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN%27%27')
        .then(response => message.reply({embeds:[new MessageEmbed().setDescription(`**Doge Coin Value** \n 1 Doge Coin equals to`).addFields({name:`EUR`,value:`${response.data.EUR}`},{name:`USD`,value:`${response.data.USD}`}).setColor(color)]}))
      }
            else if(args[0] === 'dot'){
              axios.get('https://min-api.cryptocompare.com/data/price?fsym=DOT&tsyms=USD,EUR,GBP,CHF,CAD,AUD,RUB,JPY,CNY,INR,TRY,PLN%27%27')
        .then(response =>  message.reply({embeds:[new MessageEmbed().setDescription(`**Polkadot Value** \n 1 Polkadot equals to`).addFields({name:`EUR`,value:`${response.data.EUR}`},{name:`USD`,value:`${response.data.USD}`}).setColor(color)]}))
      }
      



        // Adds the user to the set so that they can't talk for a minute
        talkedRecently.add(message.author.id);
        setTimeout(() => {
          // Removes the user from the set after a minute
          talkedRecently.delete(message.author.id);
        }, 3500);
    }

	},
};