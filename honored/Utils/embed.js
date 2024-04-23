const { MessageEmbed } = require('discord.js');

class EmbedBuilder {
    constructor(channel, string, user) {

        const Embed = new MessageEmbed(); 
        let Content = '';

        for (let str of string.split('{').values()) {
            if (str.startsWith('title:')) {
                str = str.toString().replace('}', '').replace('$v', '').replace('title:', '').trim();
                Embed.setTitle(`${str}`);
            } else if (str.startsWith('description:')) {
                str = str.toString().replace('}', '').replace('$v', '').replace('description:', '').trim();
                Embed.setDescription(`${str}`);
            } else if (str.startsWith('field:')) {
                let field = str.replace('}', '').replace('$v', '').replace('field:', '').split('&&');
                Embed.addField(`${field[0].toString().trim()}`, `${field[1].toString().trim()}`, field[2] ? field[2].toString().trim() === 'true' ? true : false : null);
            } else if (str.startsWith('author:')) {
                let author = str.replace('}', '').replace('$v', '').replace('author:', '').split('&&');
                Embed.setAuthor({ name : `${author[0]}`, iconURL : author[1] ? author[1] : null, url : author[2] ? author[2] : null });
            } else if (str.startsWith('footer:')) {
                let footer = str.replace('}', '').replace('$v', '').replace('footer:', '').split('&&');
                Embed.setFooter({ text : `${footer[0]}`, iconURL : footer[1] ? footer[1] : null });
            } else if (str.startsWith('thumbnail:')) {
                str = str.toString().replace('}', '').replace('$v', '').replace('thumbnail:', '').trim();
                Embed.setThumbnail(`${str}`);
            } else if (str.startsWith('image:')) {
                str = str.toString().replace('}', '').replace('$v', '').replace('image:', '').trim();
                Embed.setImage(`${str}`);
            } else if (str.startsWith('color:')) {
                str = str.toString().replace('}', '').replace('$v', '').replace('color:', '').trim();
                Embed.setColor(`${str}`);
            } else if (str.startsWith('timestamp')) {
                Embed.setTimestamp();
            } else if (str.startsWith('url:')) {
                str = str.toString().replace('}', '').replace('$v', '').replace('url:', '').trim();
                Embed.setURL(`${str}`);
            } else if (str.startsWith('message:')) {
                str = str.toString().replace('}', '').replace('$v', '').replace('message:', '').trim();
                Content = str;
            }
        }
        channel.send({ embeds : [Embed], content : Content.length > 0 ? Content : null }).catch(() => {
            return channel.send('Invalid embed code, try again');
        });
    }
}

module.exports = { EmbedBuilder };
