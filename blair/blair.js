console.clear()
require('dotenv/config')

const Client = new (require('./Structures/Base/Client.js'))()

Client.Start(process.env.DiscordToken)

// Crash
process.on('unhandledRejection', (Error, Reason) => { 
    console.error(Error, 'Unhandled Rejection at Promise', Reason) 
})

process.on('uncaughtException', (Error) => { 
    console.error(Error, 'Uncaught Exception thrown') 
})

module.exports = Client.Client