const { User } = require("discord.js")
const fetch = require("node-fetch");
const Cacher = require("./Vars/Cacher")
const banner_url = require("./Vars/BannerURL");
const { reCache, CacheBanner } = require("./Functions/CacheBanner");

Object.defineProperty(User.prototype, "bannerURL", {
    /**
     * 
     * @param {{
     * size?: 1024,
     * format?: "png" | "jpg" | "gif"
     * }} options 
     * @returns Promise<string|null>
     * @description Gives the banner from the user id.
     */
    value: async function(options = {
        size: 1024,
        format: "png",
    })
    {
        let userId = this.id;

        if (!options.format)
            options.format = "png";

        if (!options.size)
            options.size = 1024;

        if (Cacher.get(userId) && !reCache(userId))
            return (Cacher.get(userId)).data.url;

        const jsonData = await (this.client.api.users(userId).get());

        const banner = jsonData["banner"];

        let data = {
            color: jsonData["banner_color"],
            hash: banner,
        };

        if (banner)
        {
            const isGif = banner.startsWith("a_");

            if (!isGif)
                options.format = "png";
    
            data["url"] = `${banner_url(userId)}${banner}.${options.format}?size=${options.size}`;
        }

        if (!banner)
            data["url"] = null;

        CacheBanner(userId, data);
        return Promise.resolve(data.url);
    },
})

Object.defineProperty(User.prototype, "banner", {
    get() {
        return new Promise(async (resolve, reject) => {

            if (Cacher.get(this.id) && !reCache(this.id))
                if(Cacher.get(this.id).data.hash)
                    return (Cacher.get(this.id)).data.hash;
            
            const jsonData = await (this.client.api.users(this.id).get());
            const hash = jsonData["banner"];
            const color = jsonData["banner_color"];
            
            if(!(Cacher.get(this.id)))
            {
                let data = {
                    hash: hash,
                    color: color,
                    url: null
                }
                CacheBanner(this.id, data)
            }

            let data = (Cacher.get(this.id)).data;
            data.hash = hash;
            data.color = color;
            CacheBanner(this.id, data)

            return resolve({
                hash,
                color
            });
        })
    },
})