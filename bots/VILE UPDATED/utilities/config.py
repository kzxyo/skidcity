import random


class Emojis:
    done: str = '<:v_done:1067033981452828692>'
    fail: str = '<:v_warn:1067034029569888266>'
    reply: str = '<:vile_reply:997487959093825646>'
    dash: str = '' # '<:vile_dash:998014671107928105>'
    afk: str = '<a:vile_afk:1002923032844718102>'
    enabled: str = '<:vile_enabled:1007168449958658068>'
    disabled: str = '<:vile_disabled:1007168484159008848>'
    first_page: str = '<:v_first_page:1067034043901804564>'
    previous_page: str = '<:v_previous_page:1067034040223420467>'
    next_page: str = '<:v_next_page:1067034038386303016>'
    last_page: str = '<:v_last_page:1067034034946977792>'
    page_skip: str = '<:v_page_skip:1067034020489220166>'
    loading: str = '<a:vile_loading:1003252144377446510>'


class Colors:
    main: int = 0xb1aad8
    invisible: int = 0x2f3136


class Authorization:
    vile_token: str = 'MTAwMjI2MTkwNTYxMzc5OTUyNw.GmJ1NE.Qda-Rc35teFv-KmtfjZO-R9EORLX_qTMG4XeHU'
    vile_api: str = 'glory:mZkmMROpWJjX3'
    rival_api: str = '9c9f0f07-81fd-47f6-93cb-2894ef83012b'
    chatgpt_api: str = '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'
    wolfram_api: str = '46HPQ5-725AAXQ5TY'
    lastfm_api: str = '43693facbb24d1ac893a7d33846b15cc'


class Proxy:
    webshare: str = 'http://rxgjwaff-rotate:71wbdu4n6ke4@p.webshare.io/'
    superproxy: str = 'http://brd-customer-hl_85b99eb9-zone-static:exbqlgvrrat93@zproxy.lum-superproxy.io:22225/'
    rival: str = 'http://14a5581e0091f:a49ec48a42@181.177.115.214:12323/'


class Headers:
    user_agent: str = random.choice([
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0'
    ])


class Bot:
    prefix: str = ','
    version: str = 'v3.8.1'
    invite: str = 'https://discord.com/api/oauth2/authorize?client_id=1002261905613799527&permissions=8&scope=bot%20applications.commands'
    privacy_policy: str = 'https://vilebot.xyz/privacy'
    terms_of_service: str = 'https://vilebot.xyz/terms'
    owner_ids: set = {461914901624127489, 812126383077457921, 574429626085015573, 815742337422458890, 1002322857604419604,352190010998390796}


class DataBase:
    db: str = 'vile'
    host: str = 'localhost'
    port: int = 3306
    user: str = 'root'
    password: str = 'Glory9191'


emojis = Emojis
colors = Colors
authorization = Authorization
proxy = Proxy
headers = Headers
bot = Bot
database = DataBase
