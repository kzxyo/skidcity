module.exports = class Event {
    constructor (Client, Label) {
        this.Client = Client
        this.Label = Label

        this._Listener = this._Invoke.bind(this)
    }

    async _Invoke (...Arguments) {
        try { 
            await this.Invoke(
                ...Arguments
            ) 
        } catch (Error) { 
            console.error(Error) 
        }
    }

    StartListener () { 
        this.Client.on(
            this.Label, this._Listener
        ) 
    }
    
	StopListener() { 
        this.Client.off(
            this.Label, this._Listener
        ) 
    }
}