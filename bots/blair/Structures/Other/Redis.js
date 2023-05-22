const { createClient } = require('redis')

module.exports = class RedisHandler {
    constructor (Client) {
        this.Client = Client  
        this.Ready = false     

        this.RedisClient = createClient({
            url : process.env.RedisURL
        })

        this.Disabled = false

        this.RedisClient.on('connect', async () => {
            await this.ClearAll()
            this.Ready = true
        })
    }

    async ClearAll () {
        await this.RedisClient.flushDb()
    }

    async GetHash (Key) {
        if (!this.Ready) return null

        const Data = this.RedisClient.HGETALL(Key)

        if (!Data || !Object.keys(Data).length) return null

        return JSON.parse(JSON.stringify(Data))
    }

    async SetHash (Key, Field, Value, Time) {
        if (!this.Ready) return null

        var Bool = false

        if (typeof Value === 'object') Bool = true

        await this.RedisClient.hSet(Key, Field, Bool ? JSON.stringify(Value) : Value)

        if (Time && Time !== -1) await this.RedisClient.expire(Key, Time)
    }

    async DeleteHash (Key, Field) {
        if (!this.Ready) return null
        
        await this.RedisClient.hDel(Key, Field)
    }
}