const Command = require('../Command.js');
const search = require('youtube-search');

module.exports = class YoutubeCommand extends Command {
    constructor(client) {
        super(client, {
            name: 'youtube',
            aliases: ['yt'],
            usage: 'youtube [Video_Name]',
            description: 'Searches YouTube for the specified video',
            type: client.types.SEARCH,
            subcommands: ['youtube']
        });
    }
    async run(message, args) {
        let apiKey = "AIzaSyAr4Zo0cKHe-vFCiDZy_dmjnJkxrgcgpI8";
        const videoName = args.join(' ');
        if (!args.length) {
            return this.help(message)
        }
        const searchOptions = {
            maxResults: 1,
            key: apiKey,
            type: 'video'
        };
        if (!message.channel.nsfw) searchOptions['wasd'] = 'wasd';
        let result = await search(videoName, searchOptions)
        result = result.results[0];
        if (!result)
            return this.send_error(message, 0, 'There was no result on youtube for **' + args.join(' ') + '**');
        message.channel.send(result.link)
    }
};

