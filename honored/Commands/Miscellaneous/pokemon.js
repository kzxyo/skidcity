const axios = require('axios');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'pokemon',
        aliases: ['pokedex'],
        description: 'View information about a Pokémon',
        syntax: 'pokedex <pokemon>',
        example: 'pokedex pikachu',
        permissions: 'N/A',
        parameters: 'pokemon',
        module: 'miscellaneous'
    },
    run: async (session, message, args) => {
        if (args.length === 0) {
            return displayCommandInfo(module.exports, session, message);      
        }

        const pokemonName = args.join('-').toLowerCase();

        try {
            const response = await axios.get(`https://pokeapi.co/api/v2/pokemon/${pokemonName}`);
            const pokemonData = response.data;

            const name = pokemonData.name;
            const id = pokemonData.id;
            const types = pokemonData.types.map(type => type.type.name).join(', ');
            const abilities = pokemonData.abilities.map(ability => ability.ability.name).join(', ');

            const embed = new MessageEmbed()
                .setTitle(`${name.charAt(0).toUpperCase() + name.slice(1)} (#${id})`)
                .addField('Type(s)', types, true)
                .addField('Abilities', abilities, true)
                .setColor(session.color)
                .setThumbnail(`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${id}.png`);

            message.channel.send({ embeds: [embed] });
        } catch (error) {
            session.log('Error:', error);
            message.channel.send({ embeds: [
                new MessageEmbed()
                    .setDescription(`${session.mark} ${message.author}: That Pokémon does not exist`)
                    .setColor(session.warn)
            ]});
        }
    }
};
