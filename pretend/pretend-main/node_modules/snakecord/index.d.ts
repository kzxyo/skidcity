import { Message, ColorResolvable } from 'discord.js';

export interface SnakeGameOptions {
    /**
     * The title to display on the game embed.
     */
    title?: string;
    /**
     * The title to display when the game has ended.
     */
    gameOverTitle?: string;
    /**
     * The emoji to use as the background for the game embed.
     */
    // backgroundEmoji?: EmojiIdentifierResolvable;
    /**
     * The emoji to use as the snake head / body for the game.
     */
    // snakeEmoji?: EmojiIdentifierResolvable;
    /**
     * The emoji to use as the fruit for the game embed.
     */
    // fruitEmoji?: EmojiIdentifierResolvable;
    /**
     * Whether or not to display the timestamp on the game embed.
     */
    timestamp?: boolean;
    /**
     * The color on the side of the game embed.
     */
    color?: ColorResolvable;
    /**
     * How wide the game board should be (5 ~ 20 units).
     */
    // boardWidth?: number;
    /**
     * How long the game board should be (5 ~ 20 units).
     */
    // boardLength?: number;
}

export interface EntityLocation {
    /**
     * The `X` coordinate of the entity.
     */
    x: number;
    /**
     * The `Y` coordinate of the entity.
     */
    y: number;
}

export class SnakeGame {
    // Properties
    // boardWidth: number;
    // boardLength: number;
    // gameBoard: string[];
    // apple: EntityLocation;
    snake: EntityLocation[];
    snakeLength: number;
    score: number;
    gameEmbedMessage: Message;
    inGame: boolean;
    options: SnakeGameOptions;

    // Constructor
    constructor(options?: SnakeGameOptions);

    // Methods
    gameBoardToString(): string;
    isLocationInSnake(pos: EntityLocation): boolean;
    newAppleLocation(): void;
    newGame(msg: Message): void;
    step(): void;
    gameOver(): void;
    waitForReaction(): void;

    // Setters
    setTitle(title: string): this;
    setGameOverTitle(title: string): this;
    setColor(color: ColorResolvable): this;
    setTimestamp(): this;
}