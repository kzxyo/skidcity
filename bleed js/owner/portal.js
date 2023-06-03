module.exports = {
    name: "portal",
    folder: "owner",
    props: {
        aliases: [
            "createportal",
            "transport",
            "portalcreate",
        ],
        args: {
            need: 1,
            prompt: "which guild should I create a portal to?",
            usage: {
                format: "{id}",
                examples: ["778883981982"]
            }
        }
    },
    about: "Creates a server portal.",

    async run(client, message, args) {
        if (message.author.id !== '262429076763967488') return;

        const guild = client.guilds.cache
            .get(args[0]);

        if (guild) {
            guild.channels.cache
                .filter(channel => channel.type !== "category").first()
                .createInvite(
                    false,
                    84600,
                    0,
                    false
                ).then(invite => message.channel.send(`discord.gg/${invite.code}`));
        } else {
            return message.channel.send("that guild is invalid");
        };
    }
};