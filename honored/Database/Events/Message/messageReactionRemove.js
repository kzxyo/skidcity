module.exports = {
    configuration: {
        eventName: 'messageReactionRemove',
        devOnly: false
    },
    run: async (session, reaction, user) => {
        if (!session.reactionSnipes) {
            session.reactionSnipes = new Map();
        }

        const { message } = reaction;
        if (!message) return;

        let reactionSnipes = session.reactionSnipes.get(message.channel.id) || [];
        if (reactionSnipes.length > 20) reactionSnipes = reactionSnipes.slice(0, 19);

        reactionSnipes.unshift({
            message: message,
            reaction: reaction,
            user: user,
            removedAt: Date.now(),
        });
        session.reactionSnipes.set(message.channel.id, reactionSnipes);
    }
};
