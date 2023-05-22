module.exports = {
    name: 'test',
    description: '',
    aliases: [],
    usage: '',
    guildOnly: false,
    args: false,
    permissions: {
        bot: [],
        user: [],
    },
    execute: async (message, args, client) => {
        var Paginator = require("../Paginator.js").Paginator
        var paginator = new Paginator(client, message, [new MessageEmbed().setColor("#FFFFFF").setTitle("hi").setDescription("Hello!"), new MessageEmbed().setColor("#FFFFFF").setTitle("hi2").setDescription("Hello2!"), new MessageEmbed().setColor("#FFFFFF").setTitle("hi3").setDescription("Hello3!")], 3);
        paginator.setTimeout(60000)
        paginator.setAuthors([message.author.id])
        paginator.on("Error", function (error) {
            console.log(error)
        })
        paginator.construct()
    }
};