import type {Block, Line} from './data/types';

export type LineState = 'past' | 'active' | 'future';

/**
 * The block whose [firstLine.t, end) contains `t`, or null in gaps.
 *
 * The final block is inclusive of its end: the last frame of a reel lands
 * exactly on it, and a half-open interval would leave that frame captionless.
 */
export const activeBlock = (blocks: Block[], t: number): Block | null => {
  for (let i = 0; i < blocks.length; i++) {
    const b = blocks[i];
    const isLast = i === blocks.length - 1;
    if (t >= b.lines[0].t && (isLast ? t <= b.end : t < b.end)) return b;
  }
  return null;
};

/**
 * The lines of a block that are actually spoken before `until`.
 *
 * A block can straddle the end of a segment. The caption stack ghosts
 * upcoming lines, so without this filter the tail of the segment shows text
 * the viewer never hears — which is exactly what happened at the end of
 * reel 05's cold open.
 */
export const visibleLines = (block: Block, until: number): Line[] =>
  block.lines.filter((l) => l.t < until);

/** Per-line reveal state. The latest line whose `t` has passed is 'active'. */
export const lineState = (block: Block, t: number): LineState[] => {
  let activeIndex = -1;
  for (let i = 0; i < block.lines.length; i++) {
    if (t >= block.lines[i].t) activeIndex = i;
  }
  return block.lines.map((_, i) => {
    if (activeIndex === -1) return 'future';
    if (i < activeIndex) return 'past';
    if (i === activeIndex) return 'active';
    return 'future';
  });
};

const TARGET = 600_000;

/** 0→1 mapped to "0"→"600,000" with thousands separators. */
export const formatMoney = (progress: number): string => {
  const clamped = Math.min(1, Math.max(0, progress));
  return Math.round(clamped * TARGET).toLocaleString('en-US');
};
