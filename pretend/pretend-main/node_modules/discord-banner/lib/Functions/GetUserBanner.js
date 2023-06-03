const fetch = require("node-fetch");
const Cacher = require("../Vars/Cacher")
const banner_url = require("../Vars/BannerURL");
const { reCache, CacheBanner } = require("./CacheBanner");

/**
 * 
 * @param {string} userId The user id
 * @param {{
 * token?: string,
 * size?: 1024,
 * format?: "png" | "jpg" | "gif"
 * }} options 
 * @returns {Promise<{ hash: string | null, color: string | null, url: string | null }>}
 */
async function getUserBanner(userId, options = {
    token: Cacher.get("token"),
    size: 1024,
    format: "png"
}) {
    if (!userId)
        throw new Error(`Please ensure there's a userId`);

    let token = options.token ? options.token : Cacher.get("token");

    if (!token)
        throw new Error(`Please make sure you have a valid token.`);

    if (!options.format)
        options.format = "png";

    if (!options.size)
        options.size = 1024;

    if (Cacher.get(userId) && !reCache(userId))
        return (Cacher.get(userId)).data;

    let response = await fetch(`https://discord.com/api/v8/users/${userId}`, {
        method: 'GET',
        headers: {
            Authorization: `Bot ${token}`
        }
    });

    const status = response.status;

    if (status === 404)
        throw new Error(`Unable to find a user with id ${userId}`);

    if(status === 401)
        throw new Error(`Please ensure to have a valid token.`)

    const jsonData = await response.json();

    const banner = jsonData["banner"];

    const isColor = jsonData["banner_color"];

    let data = {
        /**
         * @deprecated
         */
        banner: banner,
        /**
         * @description
         * The hash id for banner
         */
        hash: banner,
        /**
         * @deprecated
         */
        banner_color: isColor,
        /**
         * @description
         * The hex color for banner
         */
        color: isColor,
    }

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
    return Promise.resolve(data);
}

module.exports.getUserBanner = getUserBanner;