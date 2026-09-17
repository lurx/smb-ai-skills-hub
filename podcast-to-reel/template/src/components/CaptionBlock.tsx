import {interpolate} from 'remotion';
import {TYPE} from '../theme';
import {lineState, visibleLines} from '../selectors';
import type {Block} from '../data/types';
import {EmphasisText} from './EmphasisText';

export const CaptionBlock: React.FC<{
  block: Block;
  t: number;
  /** source time this segment ends — lines starting later are never voiced here */
  until: number;
}> = ({block, t, until}) => {
  const shown = visibleLines(block, until);
  const states = lineState({...block, lines: shown}, t);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: TYPE.lineGap,
      }}
    >
      {shown.map((line, i) => {
        // 0 at the line's start, 1 after 180ms — drives the pop.
        const pop = interpolate(t, [line.t, line.t + 0.18], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        return (
          <EmphasisText
            key={i}
            text={line.text}
            style={line.style}
            state={states[i]}
            pop={pop}
          />
        );
      })}
    </div>
  );
};
