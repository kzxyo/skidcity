<div align="center">
  <br />
  <p>
    <a href="https://discord.gg/DxHvWwC"><img src="https://media.discordapp.net/attachments/682872468322648119/682872516259217418/akaneko.png" width="546" alt="Cute As Fubuki" /></a>
  </p>
  <br />
  <p>
    <a href="https://www.npmjs.com/package/akaneko"><img src="https://img.shields.io/npm/v/akaneko.svg?maxAge=3600"/></a>
    <a href="https://www.npmjs.com/package/akaneko"><img src="https://img.shields.io/npm/dt/akaneko.svg?maxAge=3600"/></a>
    <a href="https://www.npmjs.com/package/akaneko"><img src="https://badgen.net/packagephobia/install/akaneko"></a>
  </p>
</div>
Akaneko is both a SFW and NSFW Wrapper, there's hentais for you perverts to use, however do understand that I'm the only one working on this, and I hand pick images to add, so you may get repeated images! Use it for your Discord Bot, your Self Made Console Waifu, or whatever it is :3

[Discord Server](https://discord.gg/DxHvWwC) | [Repository](https://gitlab.com/weeb-squad/akaneko)

## Installation
``npm install akaneko``

## Changelogs

### v5.1.3
- Updated Typescript for succubus function, thanks Taksumaki ! ~ 
### v5.1.1
- Added Succubus Function (NSFW)
- Fixed RichEmbed to MessageEmbed (Readme)
- Removed Loli Function (ToS)

## Example(s)
**NodeJS:**
```javascript
// Akaneko //
const akaneko = require('akaneko');

async function yourFunctionName() {

  // Get SFW Neko Images, uwu //
  console.log("SFW Neko: " + await akaneko.neko());

  // Get Lewd Neko (NSFW), owo //
  console.log("Lewd Neko:" + await akaneko.lewdNeko());

  // Lewd Bomb me onii-san~~ //
  console.log("Lewd Bomb: " + await akaneko.lewdBomb(5));

  // Get other NSFW Images //
  console.log("BDSM: " + await akaneko.nsfw.bdsm());
  console.log("Maid: " + await akaneko.nsfw.maid());
  console.log("Hentai: " + await akaneko.nsfw.hentai());
}

// Call your Function! //
yourFunctionName();
```

## Legacy Function(s)
Example:
```javascript
akaneko.function() // Format
akaneko.lewdNeko() // Example
akaneko.lewdBomb(5) // Meow, I'm Example 2
```
Function | Description
---|---
lewdNeko | NSFW Neko Girls (Cat Girls)
lewdBomb(n) | Sends (n) amount of lewds! :3

## SFW Function(s)
Example:
```javascript
akaneko.function() // Format
akaneko.foxgirl() // Awoo!~ Another example!
akaneko.neko() // Meow! An Example!
```
Function | Description
---|---
neko | SFW Neko Girls (Cat Girls)
foxgirl | SFW Fox Girls (Thanks to @LamkasDev!)

## NSFW Function(s)
Example:
```javascript
akaneko.nsfw.function() // Format
akaneko.nsfw.hentai() // Example
akaneko.nsfw.feet() // Another Example
```
Function | Description
---|---
ass | I know you like anime ass~ uwu
bdsm | If you don't know what it is, search it up
blowjob | Basically an image of a girl sucking on a sharp blade!
cum | Basically sticky white stuff that is usually milked from sharpies.
doujin | Sends a random doujin page imageURL!
feet | So you like smelly feet huh?
femdom | Female Domination?
foxgirl | Girl's that are wannabe foxes, yes
gifs | Basically an animated image, so yes :3
glasses | Girls that wear glasses, uwu~
hentai | Sends a random vanilla hentai imageURL~
netorare | Wow, I won't even question your fetishes.
maid | Maids, Maid Uniforms, etc, you know what maids are :3
masturbation | Solo Queue in CSGO!
orgy | Group Lewd Acts
panties | I mean... just why? You like underwear?
pussy | The genitals of a female, or a cat, you give the meaning.
school | School Uniforms!~ Yatta~!
succubus | Spooky Succubus, oh I'm so scared~ Totally don't suck me~
tentacles | I'm sorry but, why do they look like intestines?
thighs | The top part of your legs, very hot, isn't it?
uglyBastard | The one thing most of us can all agree to hate :)
uniform |Military, Konbini, Work, Nurse Uniforms, etc!~ Sexy~
yuri | Girls on Girls, and Girl's only!<3
zettaiRyouiki | That one part of the flesh being squeeze in thigh-highs~<3

## Wallpaper Function(s)
Example:
```javascript
akaneko.nsfw.function() // NSFW Format
akaneko.nsfw.mobileWallpapers() // NSFW Example
```

Function | Description
---|---
akaneko.mobileWallpapers() | Fetch a random SFW Wallpaper! (Mobile)
akaneko.wallpapers() | Fetch a random SFW Wallpaper! (Desktop)
akaneko.nsfw.mobileWallpapers() | Fetch a random NSFW Wallpaper! (Mobile)
akaneko.nsfw.wallpapers() | Fetch a random NSFW Wallpaper! (Desktop)


## How to Resolve Promises
```javascript
// Just Calling my dear child, Akaneko //
const akaneko = require('akaneko');

// Option 1, using and calling an asyncronous function //
async function yourFunctionName() {
  console.log(await akaneko.nsfw.maid()); // Output: Some weird long link that you probably will definitely try to open //
}

// Don't forget to call your function! //
yourFunctionName();

// Option 2, Using ".then" //
akaneko.nsfw.maid().then((imageURL) => {
  console.log(imageURL);
})
```


##
Discord Bot Example
```javascript
const Discord = require('discord.js');
const akaneko = require('akaneko');

// Create New Client //
const client = new Discord.Client();

// Bot Settings //
const settings = {
  prefix: "YOUR_BOT_PREFIX",
  token: 'YOUR_BOT_TOKEN'
}

// On "Message" Event! //
client.on('message', async message => {

  // Checks if message channel is NSFW! //
  if (!message.channel.nsfw) return message.channel.send('Sorry! Not NSFW Channel!');

  // Create New Embed //
  const embed = new Discord.MessageEmbed();

  // Defines Command //
  var command = message.content.toLowerCase().slice(settings.prefix.length).split(' ')[0];

  // Onii-chan, don't reply! //
  if (!message.content.startsWith(settings.prefix) || message.author.bot) return;

  if (command == 'lewdneko') {

    // For Embed //
    embed.setImage(await akaneko.lewdNeko());
    return message.channel.send(embed);

    // For Plain Text //
    return message.channel.send(await akaneko.lewdNeko());

  } else if (command == 'maid') {

    // For Embed //
    embed.setImage(await akaneko.nsfw.maid());
    return message.channel.send(embed);

    // For Plain Text //
    return message.channel.send(await akaneko.nsfw.maid());
    
  }

}

  // Login to your bot using the bot token! (don't share it!) //
  client.login(settings.token);

});
```

## Thank Yous
- **@HanBao#8443** (For helping make lewdBomb() much more simpler and also much more efficient and fast!)
- **[@LamkasDev](https://github.com/LamkasDev)** (Helping create foxgirls() <-- sfw btw, thanks so much!)
- **[@taksumaki](https://gitlab.com/taksumaki)** TypeScript Support!

## Sources
I hand picked most of the images from the following: Discord Servers, Konachan, Patreon, Friends sending me, nHentai, etc.

## Contributing
You can contribute images by sending a list of images of a certain topic, in a JSON file to me @Ryumin#6263 (That's my discord)

## Support
[Discord Server](https://discord.gg/DxHvWwC)