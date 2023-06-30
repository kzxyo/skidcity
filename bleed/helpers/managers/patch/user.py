from discord import Member, User

import config


def badges(self) -> list[str]:
    badges = list()

    if isinstance(self, User):
        if self.banner:
            badges.append(config.Emoji.Badge.nitro)
            badges.append(config.Emoji.Badge.boost)
    elif isinstance(self, Member):
        if self.premium_since:
            badges.append(config.Emoji.Badge.nitro)
            badges.append(config.Emoji.Badge.boost)
    if self.display_avatar.is_animated() and (not config.Emoji.Badge.nitro in badges):
        badges.append(config.Emoji.Badge.nitro)

    for flag in self.public_flags:
        if flag[1] and (badge := getattr(config.Emoji.Badge, flag[0], None)):
            badges.append(badge)

    return badges


User.badges = badges
Member.badges = badges
