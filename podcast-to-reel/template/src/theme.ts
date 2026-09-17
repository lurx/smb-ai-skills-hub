import {loadFont} from '@remotion/google-fonts/Heebo';

// 'hebrew' is required or Hebrew renders as tofu.
// 'latin' is required too: digits ("600") and the course name
// ("iPhone Design Mastery") otherwise fall back to a system serif.
const {fontFamily} = loadFont('normal', {
  weights: ['900'],
  subsets: ['hebrew', 'latin'],
});

export const FONT = fontFamily;

// Sampled from the reference reel (~/Documents/סרטון השראה.mp4), not invented.
export const COLORS = {
  bg: '#1B1C20',
  text: '#FFFFFF',
  red: '#FA0000',
  gold: '#CCC0A6',
} as const;

export const LAYOUT = {
  fps: 25,
  width: 1080,
  height: 1920,
  // With the graphics layer removed there is nothing above the card, so the
  // card and captions are centred as one block instead of being pushed up.
  cardTop: 430,
  cardWidth: 1080,
  cardRadius: 32,
  captionTop: 1110,
} as const;

export const TYPE = {
  lineSize: 78,
  activeSize: 96,
  lineGap: 22,
  futureOpacity: 0.45,
  /** widest a caption line may draw, leaving an 80px margin on the 1080 canvas */
  maxLineWidth: 920,
  /** measured advance per character for Heebo 900 — see EmphasisText */
  charEm: 0.52,
} as const;
