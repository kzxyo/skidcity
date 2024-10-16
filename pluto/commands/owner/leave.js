module.exports = {
    name: 'leave', // Command name
    description: 'Forces the bot to leave the current server',
    async execute(message, args) {
        const allowedUserId = 'YOUR_USER_ID';

        if (!message.guild) {
            return message.channel.send('This command can only be used in a server.');
        }

        if (message.author.id === allowedUserId) {
            try {
                await message.channel.send('leaving.');
                await message.guild.leave();
            } catch (error) {
                console.error('Error leaving the guild:', error);
                return message.channel.send('An error occurred while trying to leave the server.');
            }
        } else {
            message.channel.send('You do not have adrians permission to use this command.');
        }
    },
};