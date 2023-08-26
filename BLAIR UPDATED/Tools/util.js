const ytdl = require('ytdl-core'), Discord = require('discord.js')

module.exports = class Util {
    constructor (bot) {
        this.bot = bot
    }

    random (characters, length = 16) {
        if (!characters) {
            characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        }

        var text = ''

        for (var i = 0; i < length; i++) {
            text += characters.charAt(Math.floor(Math.random() * characters.length))
        }

        return text
    }

    ordinal (number) {
        const suffixes = [ 'th', 'st', 'nd', 'rd' ]

        const lastDigit = number % 10, secondToLastDigit = Math.floor(number / 10) % 10

        const suffix = suffixes[(lastDigit === 1 && secondToLastDigit !== 1) ? 1 : (lastDigit === 2 && secondToLastDigit !== 1) ? 2 : (lastDigit === 3 && secondToLastDigit !== 1) ? 3 : 0]

        return number + suffix
    }

    capitalize (string) {
        return string.toLowerCase().replace(/(^|\s)\S/g, (character) => character.toUpperCase())
    }

    entry (array, select) {
        const parts = select.split(':')

        if (parts.length !== 2 || parts[0] !== 'select') {
            return false
        }

        const index = parseInt(parts[1]) - 1

        if (isNaN(index) || index < 0 || index >=  array.length) {
            return false
        }

        return array[index]
    }

    async download (url) {
        const video = await ytdl.getInfo(url)

        console.log(video)

        const dl = await ytdl.downloadFromInfo(
            video, {
                format : 'mp4'
            }
        )
        
        console.log(dl)
    }
}