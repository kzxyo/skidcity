const config = require('../../utils/json/config.json')
const fetch = require('node-fetch')
let ms = require('ms')



async function user_getrecent(user) {
    let url = `http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&user=${user}&api_key=${config.LASTFMKEY}&format=json&limit=1`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

async function user_getinfo(user) {
    let url = `http://ws.audioscrobbler.com/2.0/?method=user.getinfo&user=${user}&api_key=${config.LASTFMKEY}&format=json&limit=1`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

async function artist_getinfo(user, artist) {
    let url = `http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&user=${user}&artist=${encodeURIComponent(artist)}&api_key=${config.LASTFMKEY}&format=json&limit=1`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

async function user_getlibrary(user) {
    let url = `http://ws.audioscrobbler.com/2.0/?method=library.getartists&user=${user}&api_key=${config.LASTFMKEY}&format=json&limit=1000`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

async function get_toptracks(user) {
    let url = `http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user=${user}&api_key=${config.LASTFMKEY}&format=json&limit=1000`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

async function get_topalbums(user) {
    let url = `http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user=${user}&api_key=${config.LASTFMKEY}&format=json&limit=1000`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

async function track_search(query) {
    let url = `http://ws.audioscrobbler.com/2.0/?method=track.search&track=${encodeURIComponent(query)}&api_key=${config.LASTFMKEY}&format=json&limit=1`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

async function album_getinfo(user, artist, album) {
    let url = `http://ws.audioscrobbler.com/2.0/?method=album.getinfo&user=${user}&artist=${encodeURIComponent(artist)}&album=${encodeURIComponent(album)}&api_key=${config.LASTFMKEY}&format=json&limit=1`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

async function album_search(query) {
    let url = `http://ws.audioscrobbler.com/2.0/?method=album.search&album=${encodeURIComponent(query)}&api_key=${config.LASTFMKEY}&format=json&limit=1`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

async function track_getinfo(user, artist, track) {
    let url = `http://ws.audioscrobbler.com/2.0/?method=track.getinfo&user=${user}&artist=${encodeURIComponent(artist)}&track=${encodeURIComponent(track)}&api_key=${config.LASTFMKEY}&format=json&limit=1`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

async function artist_getCorrection(artist) {
    let url = `http://ws.audioscrobbler.com/2.0/?method=artist.getCorrection&artist=${encodeURIComponent(artist)}&api_key=${config.LASTFMKEY}&format=json&limit=1`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

async function fetch_artist_image(artist) {
    let url = `https://theaudiodb.com/api/v1/json/1/search.php?s=${artist}`;
    let settings = {
        method: "Get"
    }
    let get = fetch(url, settings).then((res) => res.json())
    return get
}

function artist_url(artist) {
    let URI = `${encodeURIComponent(artist.replace(/`?\ `?/g, `+`))}`
    return URI
}

function album_url(artist, album) {
    let URI = `${encodeURIComponent(artist.replace(/`?\ `?/g, `+`))}/${encodeURIComponent(album.replace(/`?\ `?/g, `+`))}`
    return URI
}

module.exports = {
    album_getinfo,
    album_search,
    track_search,
    user_getinfo,
    user_getlibrary,
    user_getrecent,
    artist_getCorrection,
    artist_getinfo,
    track_getinfo,
    get_topalbums,
    get_toptracks,
    fetch_artist_image,
    artist_url,
    album_url
}