const WolframAlpha = require('@dguttman/wolfram-alpha-api');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'wolfram',
        aliases: ['w'],
        description: 'Get math answers',
        syntax: 'wolfram [query]',
        example: 'wolfram 10x100',
        permissions: 'N/A',
        parameters: 'query',
        module: 'miscellaneous'
    },

    run: async (session, message, args) => {
        try {
            if (!args[0]) {
                return displayCommandInfo(module.exports, session, message);
            }

            const wolframAlphaApi = new WolframAlpha('UQTHY6-T6GYE36LHR');
            const results = await wolframAlphaApi.getShort(args.join(' '));

            if (!results) {
                return message.reply('no answer available');
            }

            message.reply(`\`${results}\``);
        } catch (error) {
            session.log('Error:', error.message);
            message.reply('no answer available');
        }
    }
};
