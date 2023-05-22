<p align="center">
  <img width="260" src="https://cdn.tolfix.com/images/TX-Small.png">
  <br/>
  NPM PACKAGE | discord-banner
</p>

# Discord-Banner
![](https://nodei.co/npm/discord-banner.svg)
<br />
![](https://img.shields.io/npm/dm/discord-banner?style=for-the-badge)
![](https://img.shields.io/npm/v/discord-banner?style=for-the-badge)
<br />
![](https://img.shields.io/github/issues/Tolfx/discord-banner?style=plastic)

Gives possibilities to get a users banner from discord.

# Installing
```txt
npm install discord-banner
```

# Discord.js support
|Version| Support|
|-------|--------|
|v13    | ✔      |
|v12    | ✔      |

# Troubleshoot
### message.author.bannerURL() is not a function?
When you create a new discord client, you need to make sure the package gets runned first before
`Works`
```js
const { Client } = require("discord.js")
require("discord-banner")();
const client = new Client;
```
`Doesn't work`
```js
const { Client } = require("discord.js")
const client = new Client;
require("discord-banner")();
```

If it doesn't work don't be afraid to ask for help on our [`discord server`](https://discord.tolfix.com/)
# Examples

With discord.js
```js
// initializes the package.
// Has to go before client!
require("discord-banner")();

// Creating a new client.
const client = new (require("discord.js").Client);

client.on("message", async (message) => {
    // Get the banner url.
    console.log(await message.author.bannerURL())
    console.log(await message.author.banner) // { hash, color };
});
```

Stand alone
```js
/**
 * Option 1
 * Include the token in the function
 */
const { getUserBanner } = require("discord-banner");

getUserBanner("a client id", {
  token: "super secret token",
}).then(banner => console.log(banner.url));

/**
 * Option 2
 * Include the token in discord-banner and cache
 */
require("discord-banner")("super secret token")
const { getUserBanner } = require("discord-banner");

getUserBanner("a client id").then(banner => console.log(banner.url));
```

# Configurations

### Caching
```js
require("discord-banner")("super secret token", {
  // Will recache each hour
  // Default 15 min
  cacheTime: 60*60*1000
})
const { getUserBanner } = require("discord-banner");

console.time("first_time");
getUserBanner("269870630738853888").then(banner => {
    console.log(banner)
    console.timeEnd("first_time") // Around 376.064ms

    console.time("cache")
    getUserBanner("269870630738853888").then(banner_two => {
        console.log(banner_two)
        console.timeEnd("cache") // Around 0.731ms
    });
});
```

# Discord
[![Discord](https://discord.com/api/guilds/833438897484595230/widget.png?style=banner4)](https://discord.gg/xHde7g93Yh)