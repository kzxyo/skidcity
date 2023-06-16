token: str = "MTExMDAxNDQ1NzY0NTYzMzU0Ng.GiVsUu.vq-2BUcKYmi0rQAJ9HEt30GfpSo44ZfuTRNQT8"
cache: str = "mem://"

class Database:
    host: str = "127.0.0.1"
    name: str = "aurora"
    user: str = "c"
    password: str = "wock"

class Colors:
    approve: int = 0xED05F1
    deny: int = 0xED05F1
    neutral: int = 0xED05F1

class Emojis:
    approve: str = "<:approve:1115395515081822330>"
    warn: str = "<:warn:1115395513567686657>"
    deny: str = "<:deny:1115395512078717008>"
    
    class Paginator:
        previous: str = "<:page_previous:1115396097574195230>"
        next: str = "<:page_next:1115396096424947784>"
        navigate: str = "<:page_navigate:1115396703898566766>"
        cancel: str = "<:page_cancel:1115397149975396413>"

class Lavalink:
    host: str = "0.0.0.0"
    port: int = 3030
    password: str = "youshallnotpass"
    spotify_client_secret: str = "d08df8638ee44bdcbfe6057a5e7ffd78"
    spotify_client_id: str = "908846bb106d4190b4cdf5ceb3d1e0e5"
