const Command = require('../../Structures/Base/command.js')

const axios = require('axios'), formdata = require('form-data')

module.exports = class OCR extends Command {
    constructor (bot) {
        super (bot, 'ocr', {
        })
    }

    async execute (bot, message, args) {
        const URL = message.attachments.first().url

        const data = new formdata()

        data.append('url', URL)
        data.append('language', 'eng')
        data.append('scale', 'true')
        data.append('OCREngine', '2')

        const results = await axios.post(`https://api.ocr.space/parse/image`, data, {
            headers : {
                apikey : process.env.OCRSPACE_API_KEY,
                ...data.getHeaders()
            },
            maxContentLength : Infinity,
            maxBodyLength : Infinity
        }).then((response) => response.data)

        let text = results?.ParsedResults?.[0]?.ParsedText

        if (text !== undefined) {
            message.channel.send(`${text}`)
        } else {
            return bot.warn(
                message, `Couldn't extract text`
            )
        }
    }
}