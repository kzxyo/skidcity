const { GoogleGenerativeAI } = require("@google/generative-ai");
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');


module.exports = {
    configuration: {
        commandName: 'gemini',
        aliases: ['gpt', 'ask', 'chatgpt'],
        description: 'Generate text with prompts',
        module: 'miscellaneous',
        syntax: 'gemini <prompt>',
        example: 'gemini Hello',
        permissions: 'N/A',
        parameters: 'prompt',
        
    },

    run: async (session, message, args) => {
        const genAI = new GoogleGenerativeAI(session.gemini);
        try {
            const prompt = args.join(' ');

            if (!prompt) {
                return displayCommandInfo(module.exports, session, message);
            }

            const model = genAI.getGenerativeModel({ model: "gemini-pro" });
            const result = await model.generateContent(prompt);
            const response = await result.response;
            const text = response.text();

            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.color)
                        .setDescription(text)
                ]
            });
        } catch (error) {
            console.error('Error generating text with Gemini:', error);
            message.channel.send({ embeds: [
                new MessageEmbed()
                    .setColor(session.warn)
                    .setDescription(`${session.mark} ${message.author}: The API returned an error`)
            ]});
        }
    }
};
