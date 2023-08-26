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

        this.shell = os.platform() === 'win32' ? 'powershell' : '/bin/bash';
        this.ps1 = os.platform() === 'win32' ? 'PS >' : '$';
        this.highlight = os.platform() === 'win32' ? 'powershell' : 'ansi';

        this.process = spawn(this.shell, os.platform() === 'win32' ? [this.code] : ['-c', this.code]);

        this.queue = [];
        this.closed = false;
        this.lastOutput = Date.now();

        backgroundReader(this.process.stdout, (line) => this.outputHandler(line));
        backgroundReader(this.process.stderr, (line) => this.errorHandler(line));
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