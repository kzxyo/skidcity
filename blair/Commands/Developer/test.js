const Command = require('../../Structures/Base/Command.js')
const { EmbedBuilder, ActionRowBuilder, ButtonBuilder } = require('discord.js')
module.exports = class Test extends Command {
    constructor (Client) {
        super (Client, 'test', {

        })
    }

    async Invoke (Client, Message, Arguments) {
        Message.delete()

        Message.channel.send({
            components : [
                new ActionRowBuilder().addComponents(
                    new ButtonBuilder({
                        label : 'Confirm',
                        emoji : '<:bConfirm:1054696921941413939>',
                        customId : 'TEST1'
                    }).setStyle('Primary'),
                    new ButtonBuilder({
                        label : 'Cancel',
                        emoji : '<:bCancel:1054696923065503744>',
                        customId : 'TEST2'
                    }).setStyle('Secondary')
                )
            ]
        })

        return
        Message.channel.send({
            embeds : [
                new EmbedBuilder({
                    title : 'VoiceMaster Interface',
                    url : 'https://blair.win',
                    description : `Control your **Voice Channel** using the interface below.\n> [**VoiceMaster**](https://blair.win) is currently bound to <#1054598506846888046>`,
                    fields : [
                        {
                            name : 'ㅤ',
                            value : `${Client.Emotes.Lock} [**Lock**](https://discord.gg/blair) the voice channel.\n${Client.Emotes.Unlock} [**Unlock**](https://discord.gg/blair) the voice channel.\n${Client.Emotes.Increase} [**Increase**](https://discord.gg/blair) the user limit.\n${Client.Emotes.Decrease} [**Decrease**](https://discord.gg/blair) the user limit.\n${Client.Emotes.Note} [**Rename**](https://discord.gg/blair) the voice channel.`,
                            inline : true
                        },
                        {
                            name : 'ㅤ',
                            value : `${Client.Emotes.Hide} [**Hide**](https://discord.gg/blair) the voice channel.\n${Client.Emotes.Reveal} [**Reveal**](https://discord.gg/blair) the voice channel.\n${Client.Emotes.Initialize} [**Initialize**](https://discord.gg/blair) a new activity.\n${Client.Emotes.Hammer} [**Disconnect**](https://discord.gg/blair) a member.\n${Client.Emotes.Microphone} [**Claim**](https://discord.gg/blair) the voice channel.`,
                            inline : true
                        }
                    ]
                }).setColor(Client.Color)
            ],
            components : [
                new ActionRowBuilder().addComponents(
                    new ButtonBuilder({
                        emoji : Client.Emotes.Lock,
                        customId : 'InterfaceLock'
                    }).setStyle('Secondary'),
                    new ButtonBuilder({
                        emoji : Client.Emotes.Unlock,
                        customId : 'InterfaceUnlock'
                    }).setStyle('Secondary'),
                    new ButtonBuilder({
                        emoji : Client.Emotes.Increase,
                        customId : 'InterfaceIncrease'
                    }).setStyle('Secondary'),
                    new ButtonBuilder({
                        emoji : Client.Emotes.Decrease,
                        customId : 'InterfaceDecrease'
                    }).setStyle('Secondary'),
                    new ButtonBuilder({
                        emoji : Client.Emotes.Note,
                        customId : 'InterfaceRename'
                    }).setStyle('Secondary')
                ),
                new ActionRowBuilder().addComponents(
                    new ButtonBuilder({
                        emoji : Client.Emotes.Hide,
                        customId : 'InterfaceHide'
                    }).setStyle('Secondary'),
                    new ButtonBuilder({
                        emoji : Client.Emotes.Reveal,
                        customId : 'InterfaceReveal'
                    }).setStyle('Secondary'),
                    new ButtonBuilder({
                        emoji : Client.Emotes.Initialize,
                        customId : 'InterfaceActivity'
                    }).setStyle('Secondary'),
                    new ButtonBuilder({
                        emoji : Client.Emotes.Hammer,
                        customId : 'InterfaceDisconnect'
                    }).setStyle('Secondary'),
                    new ButtonBuilder({
                        emoji : Client.Emotes.Microphone,
                        customId : 'InterfaceClaim'
                    }).setStyle('Secondary')
                )
            ]
        })
    }
}