export type LineStyle = 'plain' | 'red' | 'gold';

export type Line = {
  /** start time in SOURCE seconds — same timebase as the reel's transcript.json */
  t: number;
  text: string;
  style: LineStyle;
};

export type Segment = {start: number; end: number};

export type Block = {
  lines: Line[];
  /** end time in SOURCE seconds */
  end: number;
};

/**
 * Everything that differs between reels. Components read this and nothing else,
 * so a new reel is one config file plus a prepared source video.
 */
export type ReelConfig = {
  /** composition id, e.g. "Reel06" */
  id: string;
  /** file in public/, e.g. "source-06.mp4" */
  source: string;
  /** card height in px; the width is always 1080 */
  cardHeight: number;
  /** the 2-3s teaser lifted from later in the clip, in source seconds */
  coldOpen: Segment;
  /**
   * The kept runs of the clip, in source seconds, played back to back.
   * More than one entry means the speaker wandered and the detours were cut;
   * each boundary is a hard cut. Beats must not fall in the removed gaps.
   */
  body: Segment[];
  /** source seconds over which the grade moves from cold to warm */
  warmth: {from: number; to: number};
  beats: Block[];
};
