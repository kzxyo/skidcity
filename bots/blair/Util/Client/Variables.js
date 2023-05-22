module.exports = class Variables {
    constructor (Input) {
        this.Input = Input
    }

    async Replace (Options) {
        if (Options) {
            if (Options.User) {
                const User = Options.User

                this.Input = this.Input
                .replaceAll('{user.created_at}', User.createdAt)
                .replaceAll('{unix(user.created_at)}', Math.floor(User.createdTimestamp / 1000))

                .replaceAll('{user}', User.tag)
                .replaceAll('{user.name}', User.username)
                .replaceAll('{user.tag}', User.discriminator)
                .replaceAll('{user.mention}', User)
                .replaceAll('{user.id}', User.id)
                .replaceAll('{user.bot}', User.bot ? 'Yes' : 'No')
                .replaceAll('{user.avatar}', User.displayAvatarURL({ dynamic : true, size : 1024 }))
            }

            if (Options.Member) {
                const Member = Options.Member

                const Members = await Options.Guild.members.fetch()
                const JoinPosition = await Members.sort((a, b) => a.joinedAt - b.joinedAt).map((user) => user.id).indexOf(Member.id) + 1;
                const OrdinalJoinPosition = (JoinPosition.toString().endsWith(1) && !JoinPosition.toString().endsWith(11)) ? 'st' : (JoinPosition.toString().endsWith(2) && !JoinPosition.toString().endsWith(12)) ? 'nd' : (JoinPosition.toString().endsWith(3) && !JoinPosition.toString().endsWith(13)) ? 'rd' : 'th';
                
                this.Input = this.Input
                .replaceAll('{user.joined_at}', Member.joinedAt)
                .replaceAll('{unix(user.joined_at)}', Math.floor(Member.joinedTimestamp / 1000))

                .replaceAll('{user.nickname}', Member.nickname)
                .replaceAll('{user.color}', Member.displayHexColor)
                .replaceAll('{user.diplay_name}', Member.displayName)
                .replaceAll('{user.display_avatar}', Member.displayAvatarURL({ dynamic : true, size : 1024 }))
                .replaceAll('{user.boost}', 'No')
                .replaceAll('{user.boost_since}', Member.premiumSince)
                .replaceAll('{unix(user.boost_since)}', Math.floor(Member.premiumSince / 1000))
                .replaceAll('{user.highest_role}', Member.roles.highest)
                .replaceAll('{user.join_position}', JoinPosition)
                .replaceAll('{suffix(user.join_position)}', JoinPosition + OrdinalJoinPosition)
            }
        }

        return this.Input
    }
}