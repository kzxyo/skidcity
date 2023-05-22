const Subcommand = require('../../Subcommand.js');
const fetch = require('node-fetch')
const ReactionMenu = require('../../ReactionMenu.js');
const moment = require('moment');
const { MessageEmbed } = require('discord.js');
const Discord = require('discord.js')

module.exports = class Posts extends Subcommand {
    constructor(client) {
        super(client, {
            base: 'instagram',
            name: 'post',
            aliases: ['p'],
            type: client.types.SEARCH,
            usage: 'instagram post [link]',
            description: 'View a post from an instagram account',
        });
    }
    async run(message, args) {
        if (!args.length) return this.help(message)
        message.channel.sendTyping()
   

        const cookies = [
            "29901784935%3A6nBEr9GnyzcLnm%3A23"
        ]
        const sessionID = message.client.utils.rotate(cookies)

        let post = args.join(' ')
        if (!post.startsWith('https://www.instagram.com/')) return this.send_error(message, 1, `Your url is not an **instagram.com** type url`)
        if (post.includes('copy_link') || post.includes('utm_source')) {
            if (!post.includes('reel')) {
                post = post.split('/?')[0]
                post = post.split('https://www.instagram.com/p/')[1]
                post = `https://www.instagram.com/p/${post}/?__a=1`
            } else {
                post = post.split('/?')[0]
                post = post.split('https://www.instagram.com/reel/')[1]
                post = `https://www.instagram.com/p/${post}/?__a=1`
            }
        } else {
            post = post.split('https://www.instagram.com/p/')[1]
            post = `https://www.instagram.com/p/${post.replace('/', '')}/?__a=1`
        }
        const response = await  fetch(post, {
            headers: {
                'cookie': `sessionid=${sessionID}; rur=ATN`
            }})
            const data = await response.json()
            if (!data.graphql) {
                return this.api_error(message, `instagram`, `Instagram returned no data for **[${name}](https://instagram.com/${encodeURIComponent(name)})**`)
            }
                let n = 0
                if (!data) {
                    return this.api_error(message, `Instagram`, `The url provided did not return any info`)
                }
                const res = data.graphql.shortcode_media
                let tagged_users = []
                if (res.edge_media_to_tagged_user.edges.length) {
                    res.edge_media_to_tagged_user.edges.forEach(u => {
                        tagged_users.push({
                            username: `[@${encodeURIComponent(u.node.user.username)}](https://www.instagram.com/${encodeURIComponent(u.node.user.username)})`
                        })
                    })
                }
                let slides
                if (res.edge_sidecar_to_children && res.edge_sidecar_to_children.edges.length) {
                    slides = res.edge_sidecar_to_children.edges
                } else {
                    slides = []
                }
                if (!res.is_video) {
                    const embed = new MessageEmbed()
                        .setAuthor(`${res.owner.username} ${res.owner.full_name ? `(${res.owner.full_name})` : ''}`, res.owner.profile_pic_url)
                        .setTitle(`${res.owner.username} ${res.owner.is_verified ? '<:verified:859242659339042836>' : ""}`)
                        .setDescription(`${res.edge_media_to_caption.edges.length ? res.edge_media_to_caption.edges[0].node.text : ''}\n\n${tagged_users.map(x => x.username).join(', ')}`)
                        .setImage(slides[n] ? slides[n].node.display_url : res.display_url)
                        .setColor(this.hex)
                        .setFooter(`Instagram - Posted on ${moment(new Date(res.taken_at_timestamp * 1000)).format("MM-DD-YYYY")} | slide ${n + 1}/${slides.length === 0 ? 1 : slides.length}`, 'https://kmrealtyva.com/wp-content/uploads/2018/12/instagram-Logo-PNG-Transparent-Background-download.png')
                        .addField(`Comments`, `**${res.edge_media_to_parent_comment.count.toLocaleString()}**`, true)
                        .addField(`Likes`, `**${res.edge_media_preview_like.count.toLocaleString()}**`, true)
                    if (slides.length === 0) {
                        message.channel.send({ embeds: [embed] })
                    } else {
                        const json = embed.toJSON();
                        const previous = () => {
                            (n <= 0) ? n = slides.length - 1 : n--;
                            return new MessageEmbed(json)
                                .setAuthor(`${res.owner.username} ${res.owner.full_name ? `(${res.owner.full_name})` : ''}`, res.owner.profile_pic_url)
                                .setTitle(`${res.owner.username} ${res.owner.is_verified ? '<:verified:859242659339042836>' : ""}`)
                                .setDescription(`${res.edge_media_to_caption.edges.length ? res.edge_media_to_caption.edges[0].node.text : ''}\n\n${tagged_users.map(x => x.username).join(', ')}`)
                                .setImage(slides[n] ? slides[n].node.display_url : res.display_url)
                                .setColor(this.hex)
                                .setFooter(`Instagram - Posted on ${moment(new Date(res.taken_at_timestamp * 1000)).format("MM-DD-YYYY")} | slide ${n + 1}/${slides.length === 0 ? 1 : slides.length}`, 'https://kmrealtyva.com/wp-content/uploads/2018/12/instagram-Logo-PNG-Transparent-Background-download.png')
                        };
                        const next = () => {
                            (n >= slides - 1) ? n = 0 : n++;
                            return new MessageEmbed(json)
                                .setAuthor(`${res.owner.username} ${res.owner.full_name ? `(${res.owner.full_name})` : ''}`, res.owner.profile_pic_url)
                                .setTitle(`${res.owner.username} ${res.owner.is_verified ? '<:verified:859242659339042836>' : ""}`)
                                .setDescription(`${res.edge_media_to_caption.edges[0].node.text}\n\n${tagged_users.map(x => x.username).join(', ')}`)
                                .setImage(slides[n] ? slides[n].node.display_url : res.display_url)
                                .setColor(this.hex)
                                .setFooter(`Instagram - Posted on ${moment(new Date(res.taken_at_timestamp * 1000)).format("MM-DD-YYYY")} | slide ${n + 1}/${slides.length === 0 ? 1 : slides.length}`, 'https://kmrealtyva.com/wp-content/uploads/2018/12/instagram-Logo-PNG-Transparent-Background-download.png')
                        };

                        const reactions = {
                            'LEFT_ARROW': previous,
                            'STOP': null,
                            'RIGHT_ARROW': next,
                        };

                        const menu = new ReactionMenu(
                            message.client,
                            message.channel,
                            message.member,
                            embed,
                            null,
                            null,
                            reactions,
                            180000
                        );
                        menu.reactions['STOP'] = menu.stop.bind(menu);
                    }
                } else {
                    const res = data.graphql.shortcode_media
                    const embed = new MessageEmbed()
                        .setAuthor(`${res.owner.username} ${res.owner.full_name ? `(${res.owner.full_name})` : ''}`, res.owner.profile_pic_url)
                        .setTitle(`${res.owner.username} ${res.owner.is_verified ? '<:verified:859242659339042836>' : ""}`)
                        .setDescription(`${res.edge_media_to_caption.edges.length ? res.edge_media_to_caption.edges[0].node.text : ''}\n\n${tagged_users.map(x => x.username).join(', ')}`)
                        .setColor(this.hex)
                        .setFooter(`Posted on ${moment(new Date(res.taken_at_timestamp * 1000)).format("MM-DD-YYYY")} | followers: ${res.owner.edge_followed_by.count.toLocaleString()} | posts: ${res.owner.edge_owner_to_timeline_media.count.toLocaleString()}`)
                        .addField(`Comments`, `**${res.edge_media_to_parent_comment.count.toLocaleString()}**`, true)
                        .addField(`Likes`, `**${res.edge_media_preview_like.count.toLocaleString()}**`, true)
                        .addField(`Views`, `**${res.video_view_count.toLocaleString()}**`, true)
                    const video = new Discord.MessageAttachment().setFile(res.video_url)
                    message.channel.send([video, embed])
                }
    }
}