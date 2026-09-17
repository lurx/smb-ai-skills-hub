import {COLORS, FONT, TYPE} from '../theme';
import type {LineStyle} from '../data/types';
import type {LineState} from '../selectors';

export const EmphasisText: React.FC<{
  text: string;
  style: LineStyle;
  state: LineState;
  /** 0→1 pop-in progress for the active line */
  pop: number;
}> = ({text, style, state, pop}) => {
  const isActive = state === 'active';
  const requested = isActive ? TYPE.activeSize : TYPE.lineSize;
  const opacity = state === 'future' ? TYPE.futureOpacity : 1;
  const scale = isActive ? 1 + 0.15 * (1 - pop) : 1;

  // Shrink-to-fit. Lines stay on one line (the reference never wraps a boxed
  // word), so a long line would otherwise overflow the 1080px canvas —
  // "חסמו לי את הפרופיל האישי" is 24 chars and wants ~1200px at 96px.
  // CHAR_EM was measured off a render: "חסימות בפייסבוק" (15 chars @ 96px)
  // occupies ~750px, giving 750 / (15 * 96) ≈ 0.52.
  const natural = text.length * requested * TYPE.charEm;
  const size =
    natural > TYPE.maxLineWidth ? requested * (TYPE.maxLineWidth / natural) : requested;

  const boxed = style !== 'plain';
  const background =
    style === 'red' ? COLORS.red : style === 'gold' ? COLORS.gold : 'transparent';

  return (
    <div
      style={{
        fontFamily: FONT,
        fontWeight: 900,
        fontSize: size,
        color: style === 'gold' ? COLORS.bg : COLORS.text,
        opacity,
        transform: `scale(${scale})`,
        direction: 'rtl',
        textAlign: 'center',
        lineHeight: 1.15,
        padding: boxed ? '6px 26px' : 0,
        backgroundColor: background,
        textShadow: boxed ? 'none' : '0 4px 18px rgba(0,0,0,0.85)',
        whiteSpace: 'nowrap',
      }}
    >
      {text}
    </div>
  );
};
