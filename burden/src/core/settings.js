const prefix = process.env.prefix || ';'
const status = `discord.gg/burden`;



module.exports = {
  bot: {
    info: {
      prefix: process.env.prefix || ';',
      token: process.env.token,
      invLink: 'https://eden.lol/invite',
    },
    options: {
      founders: ['837726019032973372'],
      privateMode: false,
    },
    presence: {
      name: process.env.statusText || status,
      type: 'STREAMING',
      url: 'https://twitch.tv/pewdiepie'
    },
    credits: {
      developerId: '837726019032973372',
      developer: 'win#0006',
      supportServer: 'https://discord.gg/kupk5SQsQe'
    }
  }
}
