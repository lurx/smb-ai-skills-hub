import {Video} from '@remotion/media';
import {AbsoluteFill, staticFile} from 'remotion';
import {LAYOUT} from '../theme';

export const VideoCard: React.FC<{
  src: string;
  cardHeight: number;
  trimBefore: number;
  trimAfter: number;
  warmth: number;
  /** punch-in for this chunk; alternating values make hard cuts read as deliberate */
  zoom?: number;
}> = ({src, cardHeight, trimBefore, trimAfter, warmth, zoom = 1}) => {
  const saturate = 0.85 + 0.35 * warmth;
  const hue = -6 + 10 * warmth;

  return (
    <AbsoluteFill>
      {/* blurred backdrop — fills the canvas so the card never floats on flat black */}
      <AbsoluteFill style={{overflow: 'hidden'}}>
        <Video
          src={staticFile(src)}
          trimBefore={trimBefore}
          trimAfter={trimAfter}
          muted
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            filter: 'blur(48px) brightness(0.35)',
            transform: 'scale(1.2)',
          }}
        />
      </AbsoluteFill>

      {/* the card itself — carries the audio */}
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'flex-start'}}>
        <div
          style={{
            marginTop: LAYOUT.cardTop,
            width: LAYOUT.cardWidth,
            height: cardHeight,
            borderRadius: LAYOUT.cardRadius,
            overflow: 'hidden',
            boxShadow: '0 24px 80px rgba(0,0,0,0.7)',
          }}
        >
          <Video
            src={staticFile(src)}
            trimBefore={trimBefore}
            trimAfter={trimAfter}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              transform: `scale(${zoom})`,
              filter: `saturate(${saturate}) hue-rotate(${hue}deg)`,
            }}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
