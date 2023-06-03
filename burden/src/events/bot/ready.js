const client = require('../../index'),
  db = require('../../core/db.js'),
  gradient = require('gradient-string'),
  { bot } = require('../../core/settings.js'),
  isPrivate = bot.options.privateMode,
  ascii = `


██████╗░██╗░░░██╗██████╗░██████╗░███████╗███╗░░██╗
██╔══██╗██║░░░██║██╔══██╗██╔══██╗██╔════╝████╗░██║
██████╦╝██║░░░██║██████╔╝██║░░██║█████╗░░██╔██╗██║
██╔══██╗██║░░░██║██╔══██╗██║░░██║██╔══╝░░██║╚████║
██████╦╝╚██████╔╝██║░░██║██████╔╝███████╗██║░╚███║
╚═════╝░░╚═════╝░╚═╝░░╚═╝╚═════╝░╚══════╝╚═╝░░╚══╝                                                 
`;

function logAscii(bot, mode) {
  const x = `\n{!} :: Logged in as ${bot}\n{!} :: Bot is on ${mode} Mode\n\n`
  const colors = [
    gradient(`orange`, `red`)(ascii + x),
    gradient(`magenta`, `purple`)(ascii + x),
    gradient(`cyan`, `blue`)(ascii + x),
    gradient(`lime`, `yellow`)(ascii + x),
    gradient(`lime`, `cyan`)(ascii + x),
  ]
  console.log(`${colors[Math.floor(Math.random() * colors.length)]}`)
}

client.once("ready", async () => {
  await db.set(`uptime`, `${Math.floor(Date.now() / 1000)}`)
  client.user.setPresence({
    activities: [bot.presence]
  });
  
  if (isPrivate === true) logAscii(client.user.tag, 'Private')
  else if (isPrivate === false) logAscii(client.user.tag, 'Public')
});