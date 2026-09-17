import {describe, expect, it} from 'vitest';
import {REELS} from '../Root';
import {activeBlock, visibleLines} from '../selectors';
import {bodyFrames, coldOpenFrames, F, segmentFrames} from '../Reel';
import {LAYOUT, TYPE} from '../theme';
import type {ReelConfig} from './types';

/**
 * A line wider than the budget gets shrunk by EmphasisText. A little shrink is
 * fine; too much collapses the gap between the active line and its neighbours,
 * which is the contrast the whole reference style rests on. The invariant is
 * not "never shrink" — it is "stay clearly bigger than the inactive lines".
 */
const MIN_ACTIVE_RATIO = 1.12;

const shrunkActiveSize = (text: string) =>
  Math.min(TYPE.activeSize, TYPE.maxLineWidth / (text.length * TYPE.charEm));

/** Only the course name is exempt: a fixed brand string that cannot be split. */
// Brand strings that cannot be split, and so are allowed to shrink.
const UNSPLITTABLE = new Set<string>([]);

describe.each(REELS.map((c) => [c.id, c] as const))('%s', (_id, config: ReelConfig) => {
  const {beats} = config;

  it('has at least one line in every block', () => {
    for (const b of beats) expect(b.lines.length).toBeGreaterThan(0);
  });

  it('has no empty caption text', () => {
    for (const b of beats) {
      for (const l of b.lines) expect(l.text.trim().length).toBeGreaterThan(0);
    }
  });

  it('orders lines strictly within each block', () => {
    for (const b of beats) {
      for (let i = 1; i < b.lines.length; i++) {
        expect(b.lines[i].t).toBeGreaterThan(b.lines[i - 1].t);
      }
    }
  });

  it('starts every line before its block ends', () => {
    for (const b of beats) {
      for (const l of b.lines) expect(l.t).toBeLessThan(b.end);
    }
  });

  it('orders blocks without overlap', () => {
    for (let i = 1; i < beats.length; i++) {
      expect(beats[i].lines[0].t).toBeGreaterThanOrEqual(beats[i - 1].end);
    }
  });

  it('keeps every block inside one kept segment', () => {
    const stranded = beats
      .filter(
        (b) =>
          !config.body.some((seg) => b.lines[0].t >= seg.start && b.end <= seg.end),
      )
      .map((b) => `${b.lines[0].text} (${b.lines[0].t}s-${b.end}s)`);
    // A block straddling a cut would show captions for speech that was removed.
    expect(stranded).toEqual([]);
  });

  it('orders the body segments and leaves a real gap between them', () => {
    for (let i = 0; i < config.body.length; i++) {
      expect(config.body[i].end).toBeGreaterThan(config.body[i].start);
      if (i > 0) expect(config.body[i].start).toBeGreaterThan(config.body[i - 1].end);
    }
  });

  it('lifts the cold open from inside a kept segment', () => {
    expect(config.coldOpen.end).toBeGreaterThan(config.coldOpen.start);
    const inside = config.body.some(
      (seg) => config.coldOpen.start >= seg.start && config.coldOpen.end <= seg.end,
    );
    // Otherwise the teaser would show footage the body never plays.
    expect(inside).toBe(true);
  });

  /**
   * Walks every rendered frame rather than sampling. A block that ends a
   * fraction before the next begins leaves the screen captionless mid-sentence.
   * Sampling misses these — the first one found was five frames long.
   */
  it('leaves no frame without a caption', () => {
    const gaps: string[] = [];
    let f = coldOpenFrames(config);
    for (const seg of config.body) {
      for (let i = 0; i < segmentFrames(seg); i++, f++) {
        const t = seg.start + i / LAYOUT.fps;
        if (!activeBlock(beats, t)) gaps.push(`frame ${f} (source ${t.toFixed(2)}s)`);
      }
    }
    expect(gaps).toEqual([]);
  });

  it('keeps the cold open captioned too', () => {
    const gaps: string[] = [];
    for (let f = 0; f < coldOpenFrames(config); f++) {
      const t = config.coldOpen.start + f / LAYOUT.fps;
      if (!activeBlock(beats, t)) gaps.push(`cold-open frame ${f} (source ${t.toFixed(2)}s)`);
    }
    expect(gaps).toEqual([]);
  });

  /**
   * A block may straddle a segment end. Whatever is still on screen at the
   * last frame has to be text the viewer actually heard, and there has to be
   * something there at all.
   */
  it('shows only voiced lines at the end of every segment', () => {
    for (const seg of [config.coldOpen, ...config.body]) {
      const lastT = seg.start + (segmentFrames(seg) - 1) / LAYOUT.fps;
      const block = activeBlock(beats, lastT);
      expect(block, `no block at the end of ${seg.start}-${seg.end}`).not.toBeNull();
      const shown = visibleLines(block!, seg.end);
      expect(shown.length, `nothing voiced at the end of ${seg.start}-${seg.end}`)
        .toBeGreaterThan(0);
      for (const l of shown) expect(l.t).toBeLessThan(seg.end);
    }
  });

  it('keeps every line wide enough to hold the active-size contrast', () => {
    const tooWide = beats
      .flatMap((b) => b.lines)
      .filter((l) => !UNSPLITTABLE.has(l.text))
      .filter((l) => shrunkActiveSize(l.text) < TYPE.lineSize * MIN_ACTIVE_RATIO)
      .map((l) => `${l.text} (${l.text.length} chars)`);
    expect(tooWide).toEqual([]);
  });

  it('reports frame counts that add up', () => {
    expect(coldOpenFrames(config)).toBe(F(config.coldOpen.end) - F(config.coldOpen.start));
    expect(bodyFrames(config)).toBe(
      config.body.reduce((n, seg) => n + segmentFrames(seg), 0),
    );
    expect(coldOpenFrames(config)).toBeGreaterThan(0);
    expect(bodyFrames(config)).toBeGreaterThan(0);
  });
});

describe('reel registry', () => {
  it('has unique composition ids', () => {
    const ids = REELS.map((r) => r.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('gives every reel its own source file', () => {
    const srcs = REELS.map((r) => r.source);
    expect(new Set(srcs).size).toBe(srcs.length);
  });
});
