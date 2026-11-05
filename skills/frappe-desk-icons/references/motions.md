# Motion patterns

Every block below is taken from a shipped sprite (naqel/naqel), with the prefix written as `p`.
Rename `p-` to the app's prefix. Each keyframe's `0%` is the resting pose.

| Pattern | Story | Used by |
|---|---|---|
| lid | a lid lifts on a hinge | container |
| drop | something drops in and fades, then reappears | collection, mark |
| sway | hangs and swings from a point | waste bag |
| hop | a pin or object hops | pin, map, briefcase |
| march | dashes walk along a path | route |
| drive + speed | a vehicle rocks while speed lines stream | truck |
| turn | rotates around a grid point | gear, recycle |
| wrench | rocks a few degrees around a nut | maintenance |
| scan | a magnifier sweeps | inspection |
| ring | a ring spreads from a point (hover only) | regional |
| tick | a check mark is re-drawn | order, quality |
| sign | a signature is written | contract |
| write | lines grow from the left, staggered | quotation, document, id-card |
| pop | items pop in turn, staggered | dashboard, calendar days, request dots, folder-tree nodes |
| blink | windows or keys dim in turn | facility, calculator |
| lift | the top of a stack lifts | masters, boxes |
| knob | slider knobs move | sliders (setup) |
| coin | a coin drops onto a stack | pricing |
| nod | people nod in turn | customers |
| door | a door opens (transition, not animation) | home |

```css
/* lid: set the origin to the hinge end of the lid */
.p-lid { transform-box: view-box; transform-origin: 20.5px 7.3px;
	animation: p-lid 1.8s ease-in-out infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-lid { 0%, 60%, 100% { transform: rotate(0); } 25%, 40% { transform: rotate(28deg); } }

/* drop */
.p-drop { animation: p-drop 1.8s ease-in infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-drop {
	0%, 100% { transform: translateY(0); opacity: 1; }
	40% { transform: translateY(6px); opacity: 1; } 50% { transform: translateY(6px); opacity: 0; }
	55% { transform: translateY(-2px); opacity: 0; } 75% { transform: translateY(0); opacity: 1; } }

/* sway: origin at the knot */
.p-sway { transform-box: view-box; transform-origin: 12px 7px;
	animation: p-sway 1.6s ease-in-out infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-sway { 0%, 100% { transform: rotate(0); } 25% { transform: rotate(-7deg); } 75% { transform: rotate(6deg); } }

/* hop */
.p-hop { animation: p-hop 1.2s ease-in-out infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-hop { 0%, 50%, 100% { transform: translateY(0); } 20% { transform: translateY(-2.2px); } 35% { transform: translateY(0.3px); } }

/* march: on a stroked path */
.p-march { stroke-dasharray: 2.4 2.4; animation: p-march 0.8s linear infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-march { to { stroke-dashoffset: -4.8; } }

/* drive + speed: .p-drive on the body group, .p-speed on each line, lines alone in a <g> */
.p-drive { animation: p-drive 0.6s ease-in-out infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-drive { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-0.6px); } }
.p-speed { animation: p-speed 0.9s linear infinite; animation-play-state: var(--icon-motion, paused); }
.p-speed:nth-child(2) { animation-delay: 0.15s; } .p-speed:nth-child(3) { animation-delay: 0.3s; }
@keyframes p-speed { 0%, 100% { transform: translateX(0); opacity: 1; } 50% { transform: translateX(-1.6px); opacity: 0.35; } }

/* turn */
.p-gear { transform-box: view-box; transform-origin: 12px 12px;
	animation: p-turn 4s linear infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-turn { to { transform: rotate(360deg); } }

/* wrench: origin at the nut */
.p-wrench { transform-box: view-box; transform-origin: 16.5px 7.5px;
	animation: p-wrench 1.4s ease-in-out infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-wrench { 0%, 60%, 100% { transform: rotate(0); } 30% { transform: rotate(-16deg); } }

/* scan */
.p-scan { animation: p-scan 2s ease-in-out infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-scan { 0%, 100% { transform: translate(0, 0); } 30% { transform: translate(-4px, -1px); } 60% { transform: translate(-2px, -5px); } }

/* ring: wrap the ellipse in <g class="p-ring"> */
.p-ring { opacity: var(--icon-motion-opacity, 0); }
.p-ring ellipse { transform-box: fill-box; transform-origin: center;
	animation: p-ring 1.6s ease-out infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-ring { 0% { transform: scale(0.5); opacity: 1; } 100% { transform: scale(1.5); opacity: 0; } }

/* tick (sign is the same with dasharray 14 and 0%, 70%, 100% / 10%) */
.p-check { stroke-dasharray: 12; animation: p-tick 1.8s ease-out infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-tick { 0%, 50%, 100% { stroke-dashoffset: 0; } 10% { stroke-dashoffset: 12; } }

/* write */
.p-line { transform-box: fill-box; transform-origin: left center;
	animation: p-write 2s ease-out infinite; animation-play-state: var(--icon-motion, paused); }
.p-line:nth-child(2) { animation-delay: 0.2s; } .p-line:nth-child(3) { animation-delay: 0.4s; }
@keyframes p-write { 0%, 45%, 100% { transform: scaleX(1); } 8% { transform: scaleX(0); } 30% { transform: scaleX(1); } }

/* pop (add nth-child delays of 0.15s per sibling) */
.p-pop { transform-box: fill-box; transform-origin: center;
	animation: p-pop 1.8s ease-out infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-pop { 0%, 45%, 100% { transform: scale(1); } 10% { transform: scale(0.3); } 25% { transform: scale(1.15); } }

/* blink (nth-child delays of 0.15s) */
.p-blink { animation: p-blink 1.6s ease-in-out infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-blink { 0%, 45%, 100% { opacity: 1; } 20% { opacity: 0.25; } }

/* lift */
.p-lift { animation: p-lift 1.6s ease-in-out infinite; animation-play-state: var(--icon-motion, paused); }
@keyframes p-lift { 0%, 60%, 100% { transform: translateY(0); } 25% { transform: translateY(-2px); } }

/* door: a transition on hover, not an animation */
.p-door { transform-box: fill-box; transform-origin: left center;
	transform: scaleX(calc(1 - 0.7 * var(--icon-motion-opacity, 0))); transition: transform 0.3s ease; }
```

The knob, coin and nod blocks are in naqel's sprite under the same names.
