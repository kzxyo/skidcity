// Thank you Taksumaki for helping me with typescript! //
// https://gitlab.com/taksumaki //

declare module "akaneko" {
  /**
   * Returns Safe for Work Neko Images!
   * @returns image uri
   */
  export function neko(): string;

  /**
   * Returns you lewd ... and dirty ... Neko Images !
   * @returns image uri
   */
  export function lewdNeko(): string;

  /**
   * Images provided by @LamkasDev !~
   * Returns Safe for Work Foxgirl Images! Thanks @LamkasDev!
   * @returns image uri
   */
  export function foxgirl(): string;

  /**
   * Returns Sends a bomb of random images of N value!
   * Contributed by @HanBao#8443 !! Thank you so much !
   * @param total amount of lewds! :3
   * @returns image uri
   */
  export function lewdBomb(total: number): string;

  /**
   * Returns you SFW Anime Wallpapers for Desktops !
   * @returns image uri
   */
  export function wallpapers(): string;

  /**
   * Returns SFW Anime Wallpapers for Mobile Users !
   * @returns image uri
   */
  export function mobileWallpapers(): string;

  /**
   * These methods get NSFW images (lewds).
   */
  namespace nsfw {
    /**
     * I know you like anime ass~ uwu
     * @returns image uri
     */
    export function ass(): string;

    /**
     * If you don't know what it is, search it up
     * @returns image uri
     */
    export function bdsm(): string;

    /**
     * Basically an image of a girl sucking on a sharp blade!
     * @returns image uri
     */
    export function blowjob(): string;

    /**
     * Basically sticky white stuff that is usually milked from sharpies.
     * @returns image uri
     */
    export function cum(): string;

    /**
     * Sends a random doujin page imageURL!
     * @returns image uri
     */
    export function doujin(): string;

    /**
     * So you like smelly feet huh?
     * @returns image uri
     */
    export function feet(): string;

    /**
     * Female Domination?
     * @returns image uri
     */
    export function femdom(): string;

    /**
     * Girl's that are wannabe foxes, yes
     * @returns image uri
     */
    export function foxgirl(): string;

    /**
     * Basically an animated image, so yes :3
     * @returns image uri
     */
    export function gifs(): string;

    /**
     * Girls that wear glasses, uwu~
     * @returns image uri
     */
    export function glasses(): string;

    /**
     * Sends a random vanilla hentai imageURL~
     * @returns image uri
     */
    export function hentai(): string;

    /**
     * Wow, I won't even question your fetishes.
     * @returns image uri
     */
    export function netorare(): string;

    /**
     * Maids, Maid Uniforms, etc, you know what maids are :3
     * @returns image uri
     */
    export function maid(): string;

    /**
     * Solo Queue in CSGO!
     * @returns image uri
     */
    export function masturbation(): string;

    /**
     * Group Lewd Acts
     */
    export function orgy(): string;

    /**
     * I mean... just why? You like underwear?
     * @returns image uri
     */
    export function panties(): string;

    /**
     * The genitals of a female, or a cat, you give the meaning.
     * @returns image uri
     */
    export function pussy(): string;

    /**
     * School Uniforms!~ Yatta~!
     * @returns image uri
     */
    export function school(): string;

    /**
     * I'm sorry but, why do they look like intestines?
     * @returns image uri
     */
    export function tentacles(): string;

    /**
     * The top part of your legs, very hot, isn't it?
     * @returns image uri
     */
    export function thighs(): string;

    /**
     * The one thing most of us can all agree to hate :)
     * @returns image uri
     */
    export function uglyBastard(): string;

    /**
     * Military, Konbini, Work, Nurse Uniforms, etc!~ Sexy~
     * @returns image uri
     */
    export function uniform(): string;

    /**
     * Girls on Girls, and Girl's only!<3
     * @returns image uri
     */
    export function yuri(): string;

    /**
     * That one part of the flesh being squeeze in thigh-highs~<3
     * @returns image uri
     */
    export function zettaiRyouiki(): string;

    /**
     * Returns a NSFW mobile wallpaper.
     * @returns image uri
     */
    export function mobileWallpapers(): string;

    /**
     * Returns a NSFW wallpaper.
     * @returns image uri
     */
    export function wallpapers(): string;

    /**
     * Spooky Succubus, oh I'm so scared~ Totally don't suck me~
     * @returns image uri
     */
    export function succubus(): string;
  }
}
