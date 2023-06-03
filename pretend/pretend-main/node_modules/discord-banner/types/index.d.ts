import { User } from "discord.js";

declare module "discord.js" {
    export interface ClientUser
    {
        /**
         * 
         * @param {{
         * size?: 1024,
         * format?: "png" | "jpg" | "gif"
         * }} options 
         * @returns Promise<String|null>
         * @description Gives the banner from the user id.
         */
        bannerURL(options?: BannerOptions): Promise<BannerReturns["url"] | null>
        banner: Promise<Banner>;
    }

    export interface User
    {
        /**
         * 
         * @param {{
         * size?: 1024,
         * format?: "png" | "jpg" | "gif"
         * }} options 
         * @returns Promise<String|null>
         * @description Gives the banner from the user id.
         */
        bannerURL(options?: BannerOptions): Promise<BannerReturns["url"] | null>
        banner: Promise<Banner>;
    }
}

export interface BannerOptions
{
    size?: 16 | 32 | 64 | 128 | 256 | 512 | 1024;
    format?: "jpg" | "png" | "gif";
}

export interface BannerOptionsStandAlone extends BannerOptions {
    token?: string;
}

export interface Banner
{
    hash: string;
    color: string;
}

export interface BannerReturns
{
    hash: string | null;
    color: string | null;
    url: string | null;
}

/**
 * 
 * @param {string} userId The user id
 * @param {{
 * token?: string
 * size?: 1024,
 * format?: "png" | "jpg" | "gif"
 * }} options 
 * @returns Promise<{ banner: string | null, banner_color | null: string, banner_url: string | null }>
 */
export function getUserBanner(clientId: string, options?: BannerOptionsStandAlone): Promise<BannerReturns>

export interface ICacher
{
    [clientId: string]: {
        data: BannerReturns,
        cachedAt: Date
    } | {
        token: string;
        cache_time: number;
    };
} 

export const Cacher = new Map<keyof ICacher, ICacher[keyof ICacher]>();

export function banner_url<user extends string>(userId: user): `https://cdn.discordapp.com/banners/${user}/`;

export function reCache(userId: string): Boolean;

export function CacheBanner(userId: string, bannerUrl: string): void;

declare module "discord-banner"
{
    export default function (token?: string, options?: {
        cacheTime: number;
    }): void
}