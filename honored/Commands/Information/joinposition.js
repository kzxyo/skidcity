module.exports = {
    configuration: {
        commandName: "joinposition",
        aliases: ['jp'],
        description: "View the join position of a member.",
        syntax: "joinposition [member]",
        example: "joinposition @x6l",
        module: 'information',
        devOnly: false
    },
    run: async (session, message, args) => {
        const guild = message.guild;
        if (!guild) return message.channel.send("This command can only be used in a server.");

        await guild.members.fetch();

        let targetMember = message.member;
        if (message.mentions.members.size > 0) {
            targetMember = message.mentions.members.first();
        }

        const sortedMembers = Array.from(guild.members.cache.values()).sort((a, b) => a.joinedTimestamp - b.joinedTimestamp);
        const memberJoinPosition = sortedMembers.findIndex(member => member.id === targetMember.id) + 1;

        const suffix = getOrdinalSuffix(memberJoinPosition);

        message.channel.send(`${targetMember} was the ${memberJoinPosition}${suffix} member`);
    }
};

function getOrdinalSuffix(number) {
    if (number >= 10 && number <= 20) {
        return "th";
    }
    const lastDigit = number % 10;
    switch (lastDigit) {
        case 1:
            return "st";
        case 2:
            return "nd";
        case 3:
            return "rd";
        default:
            return "th";
    }
}
