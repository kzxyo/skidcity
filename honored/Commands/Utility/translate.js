const translate = require('@iamtraction/google-translate');
const { MessageEmbed } = require('discord.js');
const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');

module.exports = {
    configuration: {
        commandName: 'translate',
        aliases: ['tr'],
        description: 'Translate text between languages',
        syntax: 'translate <language> <text>',
        example: 'translate english Bună ziua',
        permissions: 'N/A',
        parameters: 'language, text',
        module: 'utility'
    },

    run: async (session, message, args) => {
        try {
            if (!args[0] || !args[1]) {
                const { displayCommandInfo } = require('/root/rewrite/Utils/command.js');
            }

            const language = args[0].toLowerCase();
            const text = args.slice(1).join(' ');

            const languages = {
                "abkhazian": "ab", "afrikaans": "af", "akan": "ak", "albanian": "sq", "amharic": "am", "arabic": "ar", "aragonese": "an", "armenian": "hy", "assamese": "as", "avaric": "av", "avestan": "ae", "aymara": "ay", "azerbaijani": "az", "bambara": "bm", "bashkir": "ba", "basque": "eu", "belarusian": "be", "bengali": "bn", "bihari": "bh", "bislama": "bi", "bosnian": "bs", "breton": "br", "bulgarian": "bg", "burmese": "my", "catalan": "ca", "chamorro": "ch", "chechen": "ce", "chichewa": "ny", "chinese": "zh", "chuvash": "cv", "cornish": "kw", "corsican": "co", "cree": "cr", "croatian": "hr", "czech": "cs", "danish": "da", "divehi": "dv", "dutch": "nl", "dzongkha": "dz", "english": "en", "esperanto": "eo", "estonian": "et", "ewe": "ee", "faroese": "fo", "fijian": "fj", "finnish": "fi", "french": "fr", "fula": "ff", "galician": "gl", "georgian": "ka", "german": "de", "greek": "el", "guarani": "gn", "gujarati": "gu", "haitian creole": "ht", "hausa": "ha", "hebrew": "he", "herero": "hz", "hindi": "hi", "hiri motu": "ho", "hungarian": "hu", "interlingua": "ia", "indonesian": "id", "interlingue": "ie", "irish": "ga", "igbo": "ig", "inupiaq": "ik", "ido": "io", "icelandic": "is", "italian": "it", "inuktitut": "iu", "japanese": "ja", "javanese": "jv", "kalaallisut": "kl", "kannada": "kn", "kashmiri": "ks", "kazakh": "kk", "khmer": "km", "kikuyu": "ki", "kinyarwanda": "rw", "kyrgyz": "ky", "komi": "kv", "kongo": "kg", "korean": "ko", "kurdish": "ku", "kwanyama": "kj", "latin": "la", "luxembourgish": "lb", "ganda": "lg", "limburgish": "li", "lingala": "ln", "lao": "lo", "lithuanian": "lt", "luba-katanga": "lu", "latvian": "lv", "manx": "gv", "macedonian": "mk", "malagasy": "mg", "malay": "ms", "malayalam": "ml", "maltese": "mt", "maori": "mi", "marathi": "mr", "marshallese": "mh", "mongolian": "mn", "nauru": "na", "navajo": "nv", "norwegian bokmål": "nb", "north ndebele": "nd", "nepali": "ne", "ndonga": "ng", "norwegian nynorsk": "nn", "norwegian": "no", "nuosu": "ii", "south ndebele": "nr", "occitan": "oc", "ojibwe": "oj", "church slavonic": "cu", "oromo": "om", "oriya": "or", "ossetian": "os", "panjabi": "pa", "pali": "pi", "persian": "fa", "polish": "pl", "pashto": "ps", "portuguese": "pt", "quechua": "qu", "romansh": "rm", "rundi": "rn", "romanian": "ro", "russian": "ru", "sanskrit": "sa", "sardinian": "sc", "sindhi": "sd", "northern sami": "se", "samoan": "sm", "sango": "sg", "serbian": "sr", "scottish gaelic": "gd", "shona": "sn", "sinhala": "si", "slovak": "sk", "slovene": "sl", "somali": "so", "southern sotho": "st", "spanish": "es", "sundanese": "su", "swahili": "sw", "swati": "ss", "swedish": "sv", "tamil": "ta", "telugu": "te", "tajik": "tg", "thai": "th", "tigrinya": "ti", "tibetan": "bo", "turkmen": "tk", "tagalog": "tl", "tswana": "tn", "tonga": "to", "turkish": "tr", "tsonga": "ts", "tatar": "tt", "twi": "tw", "tahitian": "ty", "uighur": "ug", "ukrainian": "uk", "urdu": "ur", "uzbek": "uz", "venda": "ve", "vietnamese": "vi", "volapük": "vo", "walloon": "wa", "welsh": "cy", "wolof": "wo", "western frisian": "fy", "xhosa": "xh", "yiddish": "yi", "yoruba": "yo", "zhuang": "za", "zulu": "zu"
            };

            if (!languages.hasOwnProperty(language)) {
                return message.channel.send({
                    embeds: [
                        new MessageEmbed()
                            .setColor(session.color)
                            .setTitle('Command: translate')
                            .setAuthor(`${session.user.username} help`, session.user.displayAvatarURL({ format: 'png', size: 512, dynamic: true }))
                            .setDescription('Translate text between languages\n```Syntax: translate [language] (text)\nExample: translate english Bună ziua```')
                    ]
                });
            }

            const translation = await translate(text, { to: languages[language] });

            message.channel.send({
                embeds: [
                    new MessageEmbed()
                        .setColor(session.color)
                        .setDescription(`> ${translation.text}`)
                        .setFooter(`Translated from ${translation.from.language.iso.toUpperCase()} to ${languages[language].toUpperCase()}`)
                ]
            });
        } catch (error) {
            session.log('Error:', error);
            message.reply('An error occurred while translating the text.');
        }
    }
};
