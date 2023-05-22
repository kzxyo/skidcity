
const { processors, tags, regexString } = require("./params.js")
const { MessageEmbed } = require("discord.js")
let message
function toEmbed(string) {
    let source = string.replace(/[^:]\$blank/ig, '\u200B') + '\n$end'
    const embed = new MessageEmbed()
    const errors = []
    for (tag in tags) {
        const { args, method } = tags[tag]
        const types = args.map(arg => arg.replace('?', ''))
        const regex = new RegExp(regexString.replace('@tag', tag), 'im')
        while (regex.test(source)) {
            let argContents
            const logArgs = []
            const valids = []
            const andTagRegex = /\s+\$(?:and|&)\s+/i
            let [fullmatch, content] = regex.exec(source)
            source = source.replace(new RegExp(`(?:^|\\s)\\$${tag}(?:$|\\s)`, 'i'), ' $end ')
            content = content.trim()

            if (args.length == 1) {
                argContents = [content]
            } else {
                if (andTagRegex.test(content)) {
                    argContents = content.split(andTagRegex)
                } else {
                    argContents = content.split(/\s*[\r\n]+\s*/)
                }
            }
            delete fullmatch
            delete content
            types.forEach((type, index) => {
                const fullArg = args[index]
                let arg = argContents[index]
                if (arg && !/^\$null$/i.test(arg)) {
                    const valid = processors[type](arg)
                    if (valid === 'invalid') {
                        logArgs.push('invalid: ' + type)
                    } else {
                        logArgs.push('valid: ' + type)
                        valids[index] = valid
                    }
                } else {
                    if (fullArg.startsWith('?')) {
                        logArgs.push('omit: ' + type)
                        valids[index] = null
                    } else {
                        logArgs.push('forget: ' + type)
                        valids[index] = 'GodArgumentError'
                    }
                }
            })
            let message
            if (!valids.find((arg) => arg === 'GodArgumentError')) {
                if (method !== 'message') {
                    embed[method](...valids)
                } else {
                    message = valids.toString()
                }
            } else {
                errors.push(`Error at: ${method}( ${logArgs.join(', ')})`)
            }
        }
    }
    return {
        msg: message,
        embed: embed,
        errors: errors
    }
}

module.exports = toEmbed