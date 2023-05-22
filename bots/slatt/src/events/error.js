module.exports = (client, error) => {
  if (err instanceof DiscordAPIError) {
    let stack = err.stack.split('at')
    client.logger.error(`${stack[0]}`)
  } else {
    client.logger.error(err)
  }
};
