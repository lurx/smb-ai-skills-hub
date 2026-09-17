import {Composition} from 'remotion';
import {Reel, totalFrames} from './Reel';
import {LAYOUT} from './theme';
import type {ReelConfig} from './data/types';

// One entry per reel. Everything reel-specific lives in the config file;
// the components never import a particular reel.
import {REEL_EXAMPLE} from './data/reel-EXAMPLE';

export const REELS: ReelConfig[] = [REEL_EXAMPLE];

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {REELS.map((config) => (
        <Composition
          key={config.id}
          id={config.id}
          component={Reel}
          defaultProps={{config}}
          durationInFrames={totalFrames(config)}
          fps={LAYOUT.fps}
          width={LAYOUT.width}
          height={LAYOUT.height}
        />
      ))}
    </>
  );
};
