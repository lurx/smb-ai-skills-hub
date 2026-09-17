import {describe, expect, it} from 'vitest';
import {activeBlock, formatMoney, lineState, visibleLines} from './selectors';
import type {Block} from './data/types';

const B: Block[] = [
  {end: 4.5, lines: [{t: 1.7, text: 'a', style: 'plain'}, {t: 2.7, text: 'b', style: 'plain'}]},
  {end: 6.0, lines: [{t: 4.7, text: 'c', style: 'gold'}]},
];

describe('activeBlock', () => {
  it('finds the block containing the time', () => {
    expect(activeBlock(B, 2.0)).toBe(B[0]);
    expect(activeBlock(B, 5.0)).toBe(B[1]);
  });

  it('returns null before the first block', () => {
    expect(activeBlock(B, 1.0)).toBeNull();
  });

  it('returns null in the gap between blocks', () => {
    expect(activeBlock(B, 4.6)).toBeNull();
  });

  it('returns null after the last block', () => {
    expect(activeBlock(B, 7.0)).toBeNull();
  });

  it('treats block start as inside and block end as outside', () => {
    expect(activeBlock(B, 1.7)).toBe(B[0]);
    expect(activeBlock(B, 4.5)).toBeNull();
  });

  it('includes the end of the FINAL block, so the last frame stays captioned', () => {
    expect(activeBlock(B, 6.0)).toBe(B[1]);
    expect(activeBlock(B, 6.01)).toBeNull();
  });
});

describe('lineState', () => {
  it('marks the most recently started line active', () => {
    expect(lineState(B[0], 2.0)).toEqual(['active', 'future']);
    expect(lineState(B[0], 3.0)).toEqual(['past', 'active']);
  });

  it('marks all lines future before the block starts', () => {
    expect(lineState(B[0], 0.0)).toEqual(['future', 'future']);
  });
});

describe('visibleLines', () => {
  it('drops lines that start at or after the segment end', () => {
    expect(visibleLines(B[0], 2.7).map((l) => l.text)).toEqual(['a']);
  });

  it('keeps every line when the segment outlasts the block', () => {
    expect(visibleLines(B[0], 99).map((l) => l.text)).toEqual(['a', 'b']);
  });

  it('can empty a block entirely', () => {
    expect(visibleLines(B[0], 0)).toEqual([]);
  });
});

describe('formatMoney', () => {
  it('renders zero at progress 0', () => {
    expect(formatMoney(0)).toBe('0');
  });

  it('renders the full amount with separators at progress 1', () => {
    expect(formatMoney(1)).toBe('600,000');
  });

  it('rounds to whole dollars mid-way', () => {
    expect(formatMoney(0.5)).toBe('300,000');
  });

  it('clamps out-of-range progress', () => {
    expect(formatMoney(-1)).toBe('0');
    expect(formatMoney(2)).toBe('600,000');
  });
});
