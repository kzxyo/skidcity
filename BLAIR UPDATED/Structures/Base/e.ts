import { readdir, readdirSync } from "fs";

class a {
    _loadEvents (): void {
        const directory = './app/Events';
        readdirSync('./app/events').forEach(async (category) => {
            const events = readdirSync(`${directory}/${category}`).filter((event) => event.endsWith('.ts'));

            for (const event of events.values()) {
                const i: Event = require(`${directory}/${category}/${event}`);
                const instance = new i(this, name);
                this.events.set(name, instance);
                instance.listen();
            };
        });
    };
};