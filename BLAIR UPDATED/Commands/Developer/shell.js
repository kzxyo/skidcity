const Command = require('../../Structures/Base/command.js')

const child_process = require('child_process');

module.exports = class Shell extends Command {
    constructor (bot) {
        super (bot, 'shell', {
            aliases : [ 'bash', 'sh', 'powershell', 'ps1', 'ps', 'terminal' ],
            module : 'Developer',
            guarded : true
        })
    }

    async execute (bot, message, args) {
        if (!['944099356678717500'].includes(message.author.id)) return

        const reader = new ShellReader(args.join(' '));
        let output = `${reader.highlight}\n${reader.ps1} ${args.join(' ')}\n\n`;
        const e = (str) => `\`\`\`${str}\`\`\``;

        const m = await message.channel.send(e(output))

        for await (const line of reader) {
            output += `${line}\n`;
            m.edit(e(output));
        };

        output += `\n[status] Return code ${reader.closeCode}`;
        m.edit(e(output));
    }
}

const { spawn } = require('child_process');
const os = require('os');
const readline = require('readline');

function backgroundReader (stream, callback) {
    const rl = readline.createInterface({
        input: stream, terminal: false,
    });

    rl.on('line', callback);
};

class ShellReader {
    constructor (code, timeout = 120, escapeAnsi = true) {
        this.code = code;
        this.timeout = timeout;
        this.escape = escapeAnsi;
        this.closeCode = 0;

        this.shell = os.platform() === 'win32' ? 'powershell' : '/bin/bash';
        this.ps1 = os.platform() === 'win32' ? 'PS >' : '$';
        this.highlight = os.platform() === 'win32' ? 'powershell' : 'ansi';

        this.process = spawn(this.shell, os.platform() === 'win32' ? [this.code] : ['-c', this.code]);

        this.queue = [];
        this.closed = false;
        this.lastOutput = Date.now();

        backgroundReader(this.process.stdout, (line) => this.outputHandler(line));
        backgroundReader(this.process.stderr, (line) => this.errorHandler(line));

        this.process.on('close', (code) => {
            this.closed = true;
            this.closeCode = code;
        });
    };

    cleanText (text) {
        if (this.escapeAnsi) {
            return text.replace(/\x1b\[\??(\d*)([ABCDEFGJKSThilmnsu])|;(\d+)([fH])/g, '');
        } else {
            return text;
        };
    };

    outputHandler (line) {
        this.queue.push(this.cleanText(line.toString().replace(/\r/g, '').trim()));
    };
    
    errorHandler (line) {
        this.queue.push(this.cleanText(`[stderr] ${line.toString().replace(/\r/g, '').trim()}`));
    };

    async next () {
        while (!this.closed || this.queue.length > 0) {
            if (this.queue.length > 0) {
                return this.queue.shift();
            } else {
                if (Date.now() - this.lastOutput >= this.timeout * 1000) {
                    throw new Error('Timed out while waiting for output.');
                };

                await new Promise((resolve) => setTimeout(resolve, 1000));
            };
        };

        throw new Error('The shell has been closed.')
    };

    async *[Symbol.asyncIterator] () {
        try {
            while (true) {
                yield await this.next();
                if (this.closed) break;
            };
        } catch (error) {};
    };

    close () {
        if (!this.closed) {
            this.process.kill();
            this.process.stdin.destroy();
            this.closed = true;
        };
    }
};