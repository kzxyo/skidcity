
function sendConsoleMessage(prefix, message) {
    const date = new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '')
    console.log(`${date}: `.red + `${prefix}`.yellow + ` | `.green + `${message}`.cyan)
}
module.exports = {
    sendConsoleMessage
}