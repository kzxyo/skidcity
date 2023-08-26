const redis = require('redis')

module.exports = class Redis {
    constructor () {
        this.ready = false
        this.disabled = false

        this.client = redis.createClient({
            url : process.env.REDIS_CONNECTION_URL
        })

        this.client.on('connect', () => {
            this.ready = true
        })
    }

    async flush () {
        await this.client.flushDb()
    }

    async get (key, field = null) {
        if (!this.ready) return null

        const data = field ? await this.client.hGet(key, field) : await this.client.hGetAll(key)

        return JSON.parse(JSON.stringify(data))
    }

    async set (options = {}) {
        if (!this.ready) return null
        
        const { key, field, value, expire } = options

        const str = typeof value === 'object' ? JSON.stringify(value) : value

        await this.client.hSet(key, field, str)

        if (expire && expire !== -1) await this.client.expire(key, expire)
    }

    async clearCache () {
        await this.client.flushDb()
    }
    
    async getHash (key, field = null) {
        if (!this.ready) return null

        const data = field ? await this.client.hGet(key, field) : await this.client.hGetAll(key)

        return JSON.parse(JSON.stringify(data))
    }

    async setHash (key, field, value, expiration) {
        if (!this.ready) return null

        const stringValue = typeof value === 'object' ? JSON.stringify(value) : value

        await this.client.hSet(key, field, stringValue)

        if (expiration && expiration !== -1) await this.client.expire(key, expiration)
    }

    async deleteHash (key, field) {
        if (!this.ready) return null

        await this.client.hDel(key, field)
    }

    async rangeList (key, start, stop) {
        if (!this.ready) return null

        const data = await this.client.lRange(key, start, stop)

        return data.map((value) => JSON.parse(value))
    }

    async pushList (key, value, expiration) {
        if (!this.ready) return null

        const stringValue = typeof value === 'object' ? JSON.stringify(value) : value

        await this.client.lPush(key, stringValue)

        if (expiration && expiration !== -1) await this.client.expire(key, expiration)
    }

    async trimList (key, start, stop) {
        if (!this.ready) return null

        await this.client.lTrim(key, start, stop)
    }

    async keys (prefix) {
        const keys = await this.client.keys(`${prefix}*`)

        return keys
    }

    async delete (keys) {
        if (keys.length === 0) {
            return 0
        }

        const deleted = await this.client.delete(keys)

        return deleted
    }
}