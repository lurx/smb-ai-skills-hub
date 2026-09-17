import {AbsoluteFill, Sequence, interpolate, useCurrentFrame} from 'remotion';
import {COLORS, LAYOUT} from './theme';
import type {ReelConfig, Segment} from './data/types';
import {activeBlock} from './selectors';
import {CaptionBlock} from './components/CaptionBlock';
import {VideoCard} from './components/VideoCard';

export const F = (sec: number) => Math.round(sec * LAYOUT.fps);

export const segmentFrames = (s: Segment) => F(s.end) - F(s.start);
export const coldOpenFrames = (c: ReelConfig) => segmentFrames(c.coldOpen);
export const bodyFrames = (c: ReelConfig) =>
  c.body.reduce((n, s) => n + segmentFrames(s), 0);
export const totalFrames = (c: ReelConfig) => coldOpenFrames(c) + bodyFrames(c);

/** Video card plus whichever caption block is live at this source time. */
const Chunk: React.FC<{
  config: ReelConfig;
  segment: Segment;
  /** cold open is graded warm throughout; body chunks ramp */
  fixedWarmth?: number;
  zoom?: number;
}> = ({config, segment, fixedWarmth, zoom}) => {
  const frame = useCurrentFrame();
  const t = segment.start + frame / LAYOUT.fps;
  const block = activeBlock(config.beats, t);

  const warmth =
    fixedWarmth ??
    interpolate(t, [config.warmth.from, config.warmth.to], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg}}>
      <VideoCard
        src={config.source}
        cardHeight={config.cardHeight}
        trimBefore={F(segment.start)}
        trimAfter={F(segment.end)}
        warmth={warmth}
        zoom={zoom}
      />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'flex-start'}}>
        <div style={{marginTop: LAYOUT.captionTop}}>
          {block ? <CaptionBlock block={block} t={t} until={segment.end} /> : null}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Reel: React.FC<{config: ReelConfig}> = ({config}) => {
  let from = coldOpenFrames(config);

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bg}}>
      <Sequence durationInFrames={coldOpenFrames(config)}>
        <Chunk config={config} segment={config.coldOpen} fixedWarmth={1} />
      </Sequence>

      {config.body.map((segment, i) => {
        const start = from;
        from += segmentFrames(segment);
        return (
          <Sequence key={i} from={start} durationInFrames={segmentFrames(segment)}>
            {/* alternate the punch-in so each hard cut looks like a camera
                change rather than a glitch; a single-segment reel stays at 1 */}
            <Chunk config={config} segment={segment} zoom={i % 2 === 1 ? 1.07 : 1} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
