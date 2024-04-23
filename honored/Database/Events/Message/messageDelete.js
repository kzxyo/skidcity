module.exports = {
    configuration: {
        eventName: 'messageDelete',
        devOnly: false
    },
    run: async (session, message) => {
        if (!session.snipes) {
            session.snipes = new Map();
        }

        let snipes = session.snipes.get(message.channel.id) || [];
        if (snipes.length > 20) snipes = snipes.slice(0, 19);

        snipes.unshift({
            msg: message,
            image: message.attachments.first()?.proxyURL || null,
            time: Date.now(),
        });
        session.snipes.set(message.channel.id, snipes);
    }
};
