from datetime import timedelta

from yarl import URL

from helpers.managers import ClientSession, cache
from helpers.models import TikTokProfile, TikTokProfileStatistics


@cache(ttl=timedelta(minutes=60), key="{username}")
async def profile(
    session: ClientSession,
    username: str,
) -> TikTokProfile:
    soup = await session.request(
        "GET",
        f"https://www.tiktok.com/@{username}",
        proxy=True,
        raise_for={
            404: f"No **TikTok account** found for [`@{username}`]({URL(f'https://www.tiktok.com/@{username}')})"
        },
    )

    return TikTokProfile(
        url=f"https://www.tiktok.com/@{username}",
        username=(
            soup.find(
                "h2", {"class": "tiktok-arkop9-H2ShareTitle ekmpd5l5"}
            ).text.strip()
        ),
        display_name=(
            soup.find(
                "h1", {"class": "tiktok-qpyus6-H1ShareSubTitle ekmpd5l6"}
            ).text.strip()
        ),
        description=(
            description.text
            if (
                description := (
                    soup.find("h2", {"class": "tiktok-1n8z9r7-H2ShareDesc e1457k4r3"})
                )
            )
            and (description.text != "No bio yet.")
            else None
        ),
        avatar_url=(
            soup.find("img", {"class": "tiktok-1zpj2q-ImgAvatar e1e9er4e1"}).attrs.get(
                "src"
            )
        ),
        statistics=TikTokProfileStatistics(
            verified=bool(soup.find("circle", {"fill": "#20D5EC"})),
            likes=(soup.find(title="Likes").text),
            followers=(soup.find(title="Followers").text),
            following=(soup.find(title="Following").text),
        ),
    )
