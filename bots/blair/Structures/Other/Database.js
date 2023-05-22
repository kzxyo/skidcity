const RedisClient = require('./Redis.js')
const { Sequelize } = require('sequelize')

module.exports = class Database extends Sequelize {
    constructor (Options = {}) {
        super ('')

        this.Redis = new RedisClient()

        this.Boot()
    }

    async Boot () {
        await this.authenticate().then(() => {
            console.log('Connected (Sequelize)')
        }).catch((Error) => {
            console.error('Failed Connection (Sequelize)')
        })

        this.Redis.RedisClient.connect().then(() => {
            console.log('Connected (Redis)')
        }).catch (() => {
            console.error('Failed Connection (Redis)')
        })
    }
}