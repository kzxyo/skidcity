const sharp = require('sharp');
const axios = require('axios');

module.exports = class Images {
    constructor (bot) {
        this.bot = bot
    }

async  collage(images) {
  try {
    const cellSize = await this.getCellSize(images);
    const cols = Math.ceil(Math.sqrt(images.length));
    const rows = Math.ceil(images.length / cols);
    const width = cols * cellSize;
    const height = rows * cellSize;
    const collage = sharp({ create: { width, height, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } } });
    
    const imagePromises = images.map(async (url) => {
      const response = await axios.get(url, { responseType: 'arraybuffer' }).catch(() => {});
      const image = sharp(response.data);
      return image.resize(cellSize, cellSize, { fit: 'cover' }).toBuffer();
    });
    
    const resizedImages = await Promise.all(imagePromises);
    
    resizedImages.forEach((resizedImage, i) => {
      const row = Math.floor(i / cols);
      const col = i % cols;
      const x = col * cellSize;
      const y = row * cellSize;
      collage.composite([{ input: resizedImage, left: x, top: y }]);
    });
    
    const buffer = await collage.png().toBuffer();
    
    return buffer
  } catch (error) {
    console.error('Collage', error);
    return {
      success: false,
      error: error,
    };
  }
}

async  getCellSize(images) {
  let minWidth = Infinity;
  let minHeight = Infinity;

  for (let i = 0; i < images.length; i++) {
    const url = images[i];
    const response = await axios.get(url, { responseType: 'arraybuffer' });
    const image = sharp(response.data);
    const metadata = await image.metadata();
    minWidth = Math.min(minWidth, metadata.width);
    minHeight = Math.min(minHeight, metadata.height);
  }

  return Math.min(minWidth, minHeight);
}

    }