// Importing my unborn children //
const resolve = require('../lib/resolve.js');

// Create Module //
module.exports = {

    // SFW //
    neko: function () { // Returns Safe for Work Neko Images! //

        return resolve.get('neko');

    },
    lewdNeko: function () { // Returns you lewd ... and dirty ... Neko Images ! //

        return resolve.get('lewdneko');

    },
    foxgirl: function () { // Returns Safe for Work Foxgirl Images! Thanks @LamkasDev! //

        return resolve.get('sfwfoxes'); // Images provided by @LamkasDev !~ //

    },
    lewdBomb: async function (n) { // Sends a bomb of random images of N value!
        // Contributed by @HanBao#8443 !! Thank you so much !
        if (n) {
            if (n > 20) throw new Error(`Akaneko - lewdBomb(n) | The parameter you specified is above the maximum of 20!`);
            if (isNaN(n)) throw new Error(`Akaneko - lewdBomb(n) | Parameter must be an integer!`);
            if (n == 0) n = 5 // Defaults to 5 if parameter = 0
        } else n = 5; // Defaults to 5 if no amount provided!

        const params = new Array(n).fill();
        const array = await Promise.all(params.map(param => resolve.get('random')));
        const string = array.join(' ');

        return string;

    },
    wallpapers: function () { // Returns you SFW Anime Wallpapers for Desktops ! //

        return resolve.get('wallpapers');

    },
    mobileWallpapers: function () { // Returns SFW Anime Wallpapers for Mobile Users ! //

        return resolve.get('mobileWallpapers');

    },
    nsfw: {
        ass: function () {
            return resolve.get('ass')
        },
        bdsm: function () {
            return resolve.get('bdsm')
        },
        cum: function () {
            return resolve.get('cum')
        },
        doujin: function () {
            return resolve.get('doujin')
        },
        femdom: function () {
            return resolve.get('femdom')
        },
        hentai: function () {
            return resolve.get('hentai')
        },
        maid: function () {
            return resolve.get('maid')
        },
        maids: function () {
            return resolve.get('maids')
        },
        orgy: function () {
            return resolve.get('orgy')
        },
        panties: function () {
            return resolve.get('panties')
        },
        wallpapers: function () {
            return resolve.get('nsfwwallpapers')
        },
        mobileWallpapers: function () {
            return resolve.get('nsfwmobilewallpapers')
        },
        cuckold: function () {
            return resolve.get('netorare')
        },
        netorare: function () {
            return resolve.get('netorare')
        },
        gifs: function () {
            return resolve.get('gif')
        },
        gif: function () {
            return resolve.get('gif')
        },
        blowjob: function () {
            return resolve.get('blowjob')
        },
        feet: function () {
            return resolve.get('feet')
        },
        pussy: function () {
            return resolve.get('pussy')
        },
        uglyBastard: function () {
            return resolve.get('uglybastard')
        },
        uniform: function () {
            return resolve.get('uniform')
        },
        gangbang: function () {
            return resolve.get('gangbang')
        },
        foxgirl: function () {
            return resolve.get('foxgirl')
        },
        cumslut: function () {
            return resolve.get('cumslut')
        },
        glasses: function () {
            return resolve.get('glasses')
        },
        thighs: function () {
            return resolve.get('thighs')
        },
        tentacles: function () {
            return resolve.get('tentacles')
        },
        masturbation: function () {
            return resolve.get('masturbation')
        },
        school: function () {
            return resolve.get('school')
        },
        yuri: function () {
            return resolve.get('yuri')
        },
        zettaiRyouiki: function () {
            return resolve.get('zettai-ryouiki')
        },
        succubus: function () {
            return resolve.get('succubus')
        }
    }

}