const { MessageActionRow, MessageButton, MessageEmbed, MessageSelectMenu } = require('discord.js');
class Paginator {
    constructor(client, message, embeds, pages) {
        if (!client || !message || !embeds || !pages) throw Error("<Paginator> constructor recieved an invalid set of data. Expected: Client <Object>, Message <Object>, Embeds <Array>, Pages <Number>")
        this.client = client, this.message = message, this.embeds = embeds, this.pages = pages, this.authors = [], this.timeout = 3e5, this.events = {};
        this.cid = (Math.floor(Math.random() * (90000000000 - 10000000000) + 10000000000)).toString()
    }
    setAuthors(authors) {
        try {
            if (typeof authors !== "object" || isNaN(authors.length)) throw Error("<Paginator>.setAuthors recieved an invalid set of data. Expected: Authors <Array>")
            let is_valid = true
            for (var a = 0; a < authors.length; a++) {
                if (typeof authors[a] !== "string") is_valid = false
            }
            if (is_valid === false) throw Error("<Paginator>.setAuthors recieved an invalid set of data. Expected: Authors <Array> with values of type String.")
            this.authors = authors
        } catch (e) {
            if (this.events["Error"] !== undefined) this.events["Error"]({
                type: "Error",
                source: "<Paginator>.setAuthors(...)",
                _rawError: e
            })
        }
    }
    setTimeout(timeout) {
        try {
            if (typeof timeout !== "number" || isNaN(timeout) || timeout > (60000 * 10)) throw Error("<Paginator>.setTimeout recieved an invalid set of data. Expected: Timeout <Number [<=600000]>")
            this.timeout = parseInt(timeout)
        } catch (e) {
            if (this.events["Error"] !== undefined) this.events["Error"]({
                type: "Error",
                source: "<Paginator>.setTimeout(...)",
                _rawError: e
            })
        }
    }
    on(event, callback) {
        try {
            if (typeof event !== 'string' || typeof callback !== 'function') throw Error("<Paginator>.on recieved an invalid set of data. Expected: Event <String>, Callback <Function>")
            if (![
                "arrowBtnClick",
                "exitBtnClick",
                "collectorTimeout",
                "Error",
                "menuSubmit"
            ].includes(event.toString())) throw Error("<Paginator>.on recieved an invalid set of data. Expected argument Event <String> to be in List <arrowBtnClick, exitBtnClick, collectorTimeout, Error, menuSubmit>")
            this.events[event] = callback
        } catch (e) {
            if (this.events["Error"] !== undefined) this.events["Error"]({
                type: "Error",
                source: "<Paginator>.on(...)",
                _rawError: e
            })
        }
    }
    async construct() {
        try {
            if (
                !this.client ||
                !this.message ||
                !this.embeds ||
                !this.pages ||
                (typeof this.authors !== 'object' || typeof this.authors?.length !== 'number') ||
                typeof this.timeout !== 'number' ||
                this.timeout > 600000 ||
                typeof this.events !== 'object' ||
                typeof this.cid !== 'string'
            ) throw Error("<Paginator>.construct failed to construct <Paginator> with the data set.")
            var cid = this.cid
            var row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel("1").setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(!(this.pages > 1))).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(!(this.pages > 1))), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
            var menu = new MessageSelectMenu()
                .setCustomId('pagntr_listener_menu')
                .setPlaceholder('Page 1')
            for (var v = 0; v < this.pages; v++) {
                menu.addOptions([
                    {
                        label: `Page #${v + 1}`,
                        description: '\u200B',
                        value: `pagntr_listener_menu_values_${v + 1}`,
                    }
                ])
            }
            const menu_row = new MessageActionRow()
                .addComponents(
                    menu
                );
            this.msg = await this.message.reply({ embeds: [this.embeds[0]], components: [menu_row, row, row2] })
            const collector = this.msg.createMessageComponentCollector({ componentType: 'BUTTON', time: this.timeout });
            var current_page = 1
            var ended_normal = false
            collector.on('collect', async i => {
                if (!this.authors.includes(i.user.id.toString())) return await i.reply({
                    embeds: [new MessageEmbed()
                        .setColor("#8B0000")
                        .setAuthor({ name: "An Error Occurred" })
                        .setTitle("Unauthorized Interaction")
                        .setDescription(`You don't have permission to interact with this paginator.`)
                        .setTimestamp()
                        .setFooter({
                            text: `${client.user.username}`,
                            iconURL: client.user.displayAvatarURL()
                        })], ephemeral: true
                })
                if (!i.customId.includes(this.cid)) return await i.reply({
                    embeds: [new MessageEmbed()
                        .setColor("#8B0000")
                        .setAuthor({ name: "An Error Occurred" })
                        .setTitle("Inaccessible Paginator")
                        .setDescription(`The Paginator ID included in this interaction does not match the one asigned to this paginator.`)
                        .setTimestamp()
                        .setFooter({
                            text: `${client.user.username}`,
                            iconURL: client.user.displayAvatarURL()
                        })], ephemeral: true
                })
                await i.deferUpdate()
                var id = i.customId.split(":")[0]
                if (id === "pagntr_listener_exit_pagntr") {
                    ended_normal = true
                    if (this.events["exitBtnClick"] !== undefined) this.events["exitBtnClick"]({
                        type: "ButtonClick",
                        button: "exit",
                        _rawInteraction: i
                    })
                    row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel("1").setStyle("PRIMARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(!0)), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER").setDisabled(!0));
                    await this.msg.edit({ embeds: [this.embeds[current_page - 1]], components: [row, row2] })
                    collector.stop()
                }
                if (id === "pagntr_listener_right_far") {
                    if (current_page === this.pages || current_page > this.pages) return;
                    if (this.events["arrowBtnClick"] !== undefined) this.events["arrowBtnClick"]({
                        type: "ButtonClick",
                        button: "right-far",
                        _rawInteraction: i
                    })
                    current_page = this.pages
                    var row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel(`${current_page}`).setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(!0)), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
                    await this.msg.edit({ embeds: [this.embeds[current_page - 1]], components: [menu_row, row, row2] })
                }
                if (id === "pagntr_listener_left_far") {
                    if (current_page === 1) return;
                    if (this.events["arrowBtnClick"] !== undefined) this.events["arrowBtnClick"]({
                        type: "ButtonClick",
                        button: "left-far",
                        _rawInteraction: i
                    })
                    current_page = 1
                    var row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel("1").setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY")), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
                    await this.msg.edit({ embeds: [this.embeds[0]], components: [menu_row, row, row2] })
                }
                if (id === "pagntr_listener_left") {
                    if (current_page === 1) return;
                    if (this.events["arrowBtnClick"] !== undefined) this.events["arrowBtnClick"]({
                        type: "ButtonClick",
                        button: "left",
                        _rawInteraction: i
                    })
                    current_page--
                    row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(1 === current_page)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(1 === current_page)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel(`${current_page}`).setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY")), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
                    await this.msg.edit({ embeds: [this.embeds[current_page - 1]], components: [menu_row, row, row2] })
                }
                if (id === "pagntr_listener_right") {
                    if (current_page === this.pages) return;
                    if (this.events["arrowBtnClick"] !== undefined) this.events["arrowBtnClick"]({
                        type: "ButtonClick",
                        button: "right",
                        _rawInteraction: i
                    })
                    current_page++
                    row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel(`${current_page}`).setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(current_page === this.pages)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(current_page === this.pages)), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
                    await this.msg.edit({ embeds: [this.embeds[current_page - 1]], components: [menu_row, row, row2] })
                }
            });

            collector.on('end', async collected => {
                if (ended_normal === true) return;
                if (this.events["collectorTimeout"] !== undefined) this.events["collectorTimeout"]({
                    type: "CollectorTimeout",
                    _rawCollected: collected
                })
                row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel("1").setStyle("PRIMARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(!0)), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER").setDisabled(!0));
                await this.msg.edit({ embeds: [this.embeds[current_page - 1]], components: [row, row2] })
                collector.stop()
            });
            const menu_collector = this.msg.createMessageComponentCollector({ componentType: 'SELECT_MENU', time: this.timeout });
            menu_collector.on("collect", async i => {
                if (!this.authors.includes(i.user.id.toString())) return await i.reply({
                    embeds: [new MessageEmbed()
                        .setColor("#8B0000")
                        .setAuthor({ name: "An Error Occurred" })
                        .setTitle("Unauthorized Interaction")
                        .setDescription(`You don't have permission to interact with this paginator.`)
                        .setTimestamp()
                        .setFooter({
                            text: `${client.user.username}`,
                            iconURL: client.user.displayAvatarURL()
                        })], ephemeral: true
                })
                await i.deferUpdate()
                var selected_page = i.values[0].toString().replace("pagntr_listener_menu_values_", "")
                if (this.events["menuSubmit"] !== undefined) this.events["menuSubmit"]({
                    type: "menuSubmit",
                    page: selected_page,
                    _rawInteraction: i
                })
                current_page = parseInt(selected_page)
                row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(1 === current_page)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(1 === current_page)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel(`${current_page}`).setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(current_page === this.pages)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(current_page === this.pages)), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
                await this.msg.edit({ embeds: [this.embeds[current_page - 1]], components: [menu_row, row, row2] })
            })
        } catch (e) {
            if (this.events["Error"] !== undefined) this.events["Error"]({
                type: "Error",
                source: "<Paginator>.construct(...)",
                _rawError: e
            })
        }
    }
}





class MultiMenuPaginator {
    constructor(client, message, embeds, categories) {
        var pages = categories[0].number_of_embeds
        if (!client || !message || !embeds || !pages) throw Error("<Paginator> constructor recieved an invalid set of data. Expected: Client <Object>, Message <Object>, Embeds <Array>, Pages <Number>")
        this.client = client, this.message = message, this.embeds = embeds, this.pages = pages, this.authors = [], this.timeout = 3e5, this.events = {};
        this.cid = (Math.floor(Math.random() * (90000000000 - 10000000000) + 10000000000)).toString()
        this.categories = categories
    }
    setAuthors(authors) {
        try {
            if (typeof authors !== "object" || isNaN(authors.length)) throw Error("<Paginator>.setAuthors recieved an invalid set of data. Expected: Authors <Array>")
            let is_valid = true
            for (var a = 0; a < authors.length; a++) {
                if (typeof authors[a] !== "string") is_valid = false
            }
            if (is_valid === false) throw Error("<Paginator>.setAuthors recieved an invalid set of data. Expected: Authors <Array> with values of type String.")
            this.authors = authors
        } catch (e) {
            if (this.events["Error"] !== undefined) this.events["Error"]({
                type: "Error",
                source: "<Paginator>.setAuthors(...)",
                _rawError: e
            })
        }
    }
    setTimeout(timeout) {
        try {
            if (typeof timeout !== "number" || isNaN(timeout) || timeout > (60000 * 10)) throw Error("<Paginator>.setTimeout recieved an invalid set of data. Expected: Timeout <Number [<=600000]>")
            this.timeout = parseInt(timeout)
        } catch (e) {
            if (this.events["Error"] !== undefined) this.events["Error"]({
                type: "Error",
                source: "<Paginator>.setTimeout(...)",
                _rawError: e
            })
        }
    }
    on(event, callback) {
        try {
            if (typeof event !== 'string' || typeof callback !== 'function') throw Error("<Paginator>.on recieved an invalid set of data. Expected: Event <String>, Callback <Function>")
            if (![
                "arrowBtnClick",
                "exitBtnClick",
                "collectorTimeout",
                "menuSubmit",
                "Error"
            ].includes(event.toString())) throw Error("<Paginator>.on recieved an invalid set of data. Expected argument Event <String> to be in List <arrowBtnClick, exitBtnClick, collectorTimeout, Error, menuSubmit>")
            this.events[event] = callback
        } catch (e) {
            if (this.events["Error"] !== undefined) this.events["Error"]({
                type: "Error",
                source: "<Paginator>.on(...)",
                _rawError: e
            })
        }
    }
    async construct() {
        try {
            if (
                !this.client ||
                !this.message ||
                !this.embeds ||
                !this.pages ||
                (typeof this.authors !== 'object' || typeof this.authors?.length !== 'number') ||
                typeof this.timeout !== 'number' ||
                this.timeout > 600000 ||
                typeof this.events !== 'object' ||
                typeof this.cid !== 'string'
            ) throw Error("<Paginator>.construct failed to construct <Paginator> with the data set.")
            var cid = this.cid
            var row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel("1").setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(!(this.pages > 1))).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(!(this.pages > 1))), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
            var menu = new MessageSelectMenu()
                .setCustomId('pagntr_listener_menu')
                .setPlaceholder(`${this.categories[0].name}`)
            for (var v = 0; v < this.categories.length; v++) {
                if (this.categories[v].description.length > 75) this.categories[v].description = this.categories[v].description.substring(0, 75) + "..."
                menu.addOptions([
                    {
                        label: `${this.categories[v].name}`,
                        description: `${this.categories[v].description}`,
                        emoji: this.categories[v].emoji,


                        value: `pagntr_listener_menu_values_${v}`,
                    }
                ])
            }
            const menu_row = new MessageActionRow()
                .addComponents(
                    menu
                );
            //this.msg = await this.message.reply({ embeds: [this.embeds[0][0]], components: [menu_row, row, row2] })
            await this.message.edit({ embeds: [this.embeds[0][0]], components: [menu_row, row, row2] })
            this.msg = this.message
            const collector = this.msg.createMessageComponentCollector({ componentType: 'BUTTON', time: this.timeout });
            var current_cat = 0
            var current_page = 1
            var ended_normal = false
            collector.on('collect', async i => {
                if (!this.authors.includes(i.user.id.toString())) return await i.reply({
                    embeds: [new MessageEmbed()
                        .setColor("#8B0000")
                        .setAuthor({ name: "An Error Occurred" })
                        .setTitle("Unauthorized Interaction")
                        .setDescription(`You don't have permission to interact with this paginator.`)
                        .setTimestamp()
                        .setFooter({
                            text: `${client.user.username}`,
                            iconURL: client.user.displayAvatarURL()
                        })], ephemeral: true
                })
                if (!i.customId.includes(this.cid)) return await i.reply({
                    embeds: [new MessageEmbed()
                        .setColor("#8B0000")
                        .setAuthor({ name: "An Error Occurred" })
                        .setTitle("Inaccessible Paginator")
                        .setDescription(`The Paginator ID included in this interaction does not match the one asigned to this paginator.`)
                        .setTimestamp()
                        .setFooter({
                            text: `${client.user.username}`,
                            iconURL: client.user.displayAvatarURL()
                        })], ephemeral: true
                })
                await i.deferUpdate()
                var id = i.customId.split(":")[0]
                if (id === "pagntr_listener_exit_pagntr") {
                    ended_normal = true
                    if (this.events["exitBtnClick"] !== undefined) this.events["exitBtnClick"]({
                        type: "ButtonClick",
                        button: "exit",
                        _rawInteraction: i
                    })
                    row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel("1").setStyle("PRIMARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(!0)), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER").setDisabled(!0));
                    await this.msg.edit({ embeds: [this.embeds[current_cat][current_page - 1]], components: [row, row2] })
                    collector.stop()
                }
                if (id === "pagntr_listener_right_far") {
                    if (current_page === this.pages || current_page > this.pages) return;
                    if (this.events["arrowBtnClick"] !== undefined) this.events["arrowBtnClick"]({
                        type: "ButtonClick",
                        button: "right-far",
                        _rawInteraction: i
                    })
                    current_page = this.pages
                    var row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel(`${current_page}`).setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(!0)), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
                    await this.msg.edit({ embeds: [this.embeds[current_cat][current_page - 1]], components: [menu_row, row, row2] })
                }
                if (id === "pagntr_listener_left_far") {
                    if (current_page === 1) return;
                    if (this.events["arrowBtnClick"] !== undefined) this.events["arrowBtnClick"]({
                        type: "ButtonClick",
                        button: "left-far",
                        _rawInteraction: i
                    })
                    current_page = 1
                    var row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel("1").setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY")), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
                    await this.msg.edit({ embeds: [this.embeds[current_cat][0]], components: [menu_row, row, row2] })
                }
                if (id === "pagntr_listener_left") {
                    if (current_page === 1) return;
                    if (this.events["arrowBtnClick"] !== undefined) this.events["arrowBtnClick"]({
                        type: "ButtonClick",
                        button: "left",
                        _rawInteraction: i
                    })
                    current_page--
                    row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(1 === current_page)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(1 === current_page)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel(`${current_page}`).setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY")), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
                    await this.msg.edit({ embeds: [this.embeds[current_cat][current_page - 1]], components: [menu_row, row, row2] })
                }
                if (id === "pagntr_listener_right") {
                    if (current_page === this.pages) return;
                    if (this.events["arrowBtnClick"] !== undefined) this.events["arrowBtnClick"]({
                        type: "ButtonClick",
                        button: "right",
                        _rawInteraction: i
                    })
                    current_page++
                    row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel(`${current_page}`).setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(current_page === this.pages)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(current_page === this.pages)), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
                    await this.msg.edit({ embeds: [this.embeds[current_cat][current_page - 1]], components: [menu_row, row, row2] })
                }
            });

            collector.on('end', async collected => {
                if (ended_normal === true) return;
                if (this.events["collectorTimeout"] !== undefined) this.events["collectorTimeout"]({
                    type: "CollectorTimeout",
                    _rawCollected: collected
                })
                row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel("1").setStyle("PRIMARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(!0)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(!0)), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER").setDisabled(!0));
                await this.msg.edit({ embeds: [this.embeds[current_cat][current_page - 1]], components: [row, row2] })
                collector.stop()
            });
            const menu_collector = this.msg.createMessageComponentCollector({ componentType: 'SELECT_MENU', time: this.timeout });
            menu_collector.on("collect", async i => {
                if (!this.authors.includes(i.user.id.toString())) return await i.reply({
                    embeds: [new MessageEmbed()
                        .setColor("#8B0000")
                        .setAuthor({ name: "An Error Occurred" })
                        .setTitle("Unauthorized Interaction")
                        .setDescription(`You don't have permission to interact with this paginator.`)
                        .setTimestamp()
                        .setFooter({
                            text: `${client.user.username}`,
                            iconURL: client.user.displayAvatarURL()
                        })], ephemeral: true
                })
                await i.deferUpdate()
                var selected_cat = i.values[0].toString().replace("pagntr_listener_menu_values_", "")
                if (this.events["menuSubmit"] !== undefined) this.events["menuSubmit"]({
                    type: "menuSubmit",
                    category: selected_cat,
                    page: 1,
                    _rawInteraction: i
                })
                current_cat = parseInt(selected_cat)
                current_page = 1
                this.pages = this.categories[current_cat].number_of_embeds
                row = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_left_far:${cid}`).setLabel(`1 ←`).setStyle("SECONDARY").setDisabled(1 === current_page)).addComponents(new MessageButton().setCustomId(`pagntr_listener_left:${cid}`).setLabel(`◄`).setStyle("SECONDARY").setDisabled(1 === current_page)).addComponents(new MessageButton().setCustomId(`pagntr_listener_page_num:${cid}`).setLabel("1").setStyle("PRIMARY")).addComponents(new MessageButton().setCustomId(`pagntr_listener_right:${cid}`).setLabel(`►`).setStyle("SECONDARY").setDisabled(current_page === this.pages)).addComponents(new MessageButton().setCustomId(`pagntr_listener_right_far:${cid}`).setLabel(`→ ${this.pages}`).setStyle("SECONDARY").setDisabled(current_page === this.pages)), row2 = new MessageActionRow().addComponents(new MessageButton().setCustomId(`pagntr_listener_exit_pagntr:${cid}`).setLabel("Close Paginator").setStyle("DANGER"));
                await this.msg.edit({ embeds: [this.embeds[current_cat][current_page - 1]], components: [menu_row, row, row2] })
            })
        } catch (e) {
            if (this.events["Error"] !== undefined) this.events["Error"]({
                type: "Error",
                source: "<Paginator>.construct(...)",
                _rawError: e
            })
        }
    }
}
module.exports.Paginator = Paginator
module.exports.MultiMenuPaginator = MultiMenuPaginator