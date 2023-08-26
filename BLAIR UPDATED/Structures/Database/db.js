const { Sequelize } = require('sequelize'), Redis = require('./redis.js')

module.exports = class DB extends Sequelize {
    constructor (options = {}) {
        super (process.env.POSTGRESQL_CONNECTION_URL, options)

        this.redis = new Redis()

        this.connect()
    }

    async connect () {
        await this.authenticate().then(console.log('Connected to PostgreSQL')).catch(console.error)
        await this.redis.client.connect().then(console.log('Connected to Redis')).catch(console.error)
    }
}