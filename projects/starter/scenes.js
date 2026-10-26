// Starter project: one reel, about Repo2Reels itself. Copy it for your own product with
//   python3 make.py new yourproduct
// then change the lines in project.json and what is on screen here.
//
// A reel is one REELS entry. setup() runs once: it builds the cards, reads when words are spoken, and queues
// the sound effects. scene(t) runs for every frame: it poses everything for time t, in seconds.
// docs/writing-scenes.md lists every helper (enter, deck, wt, ev, RN.circle ...).

// Small line icons, drawn in the colour of the text around them.
const ico = (d, size = 40) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;
const I_CHECK = ico('<path d="M5 12.5l4.5 4.5L19 7.5"/>', 38);
const I_NOKEY = ico('<circle cx="8" cy="15" r="4.2"/><path d="M11 12l8.5-8.5M16 7l2.6 2.6M13.6 9.4l1.8 1.8"/><path d="M3 3l18 18" stroke="#a84720"/>', 54);
const I_NOGPU = ico('<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2.5v3.5M15 2.5v3.5M9 18v3.5M15 18v3.5M2.5 9h3.5M2.5 15h3.5M18 9h3.5M18 15h3.5"/><path d="M3 3l18 18" stroke="#a84720"/>', 54);
const I_LAPTOP = ico('<rect x="4" y="5" width="16" height="11" rx="1.5"/><path d="M2 19.5h20"/>', 54);

REELS.r1 = {
  bug: 'Starter reel',                                   // the corner chip in the day scene
  label: 'Turn your product into reels',                 // the end card's headline
  foot: 'Made with Repo2Reels from projects/starter. MIT licence: free to use, change and share.',
  setup() {
    std(this, 5);   // the iris into the day scene just before line 2, the end card just before line 5

    // ---- night scene: the hook, and a terminal card typing the command that made this reel
    const CMD = 'python3 make.py projects/starter';
    hookSetup(this, ['Your repo can', 'make its own', '<g>reels.</g>'], { max: 170, top: 300, extra: `
      <div class="glass ncard" id="term" style="top:930px"><div class="eb">Terminal</div>
        <div class="in mono" id="cmd" style="margin-top:20px;font-size:32px"></div>
        <div class="mono" id="made" style="margin-top:22px;font-size:25px;display:flex;align-items:center;gap:12px;color:rgba(255,255,255,.8)">
          <span style="color:var(--goldlight);display:flex">${I_CHECK}</span>repo2reels-reel-1-your-repo-reels.mp4</div></div>` });
    this.ty = [.55, 1.75];                                                  // typing runs from 0.55 s to 1.75 s
    for (let k = 0; k < CMD.length; k += 3) ev(this.ty[0] + k / CMD.length * (this.ty[1] - this.ty[0]), 'key');
    this.tmade = wt(1, 'own'); ev(this.tmade, 'pop');                      // the finished file appears on "own"
    this.circ = RN.circle(this.hw[6], { seed: 4, pad: 14, width: 7 });     // hw: the hook's words; [6] is "reels."
    this.tc = wt(1, 'reels'); ev(this.tc, 'scribble');

    // ---- day scene: three cards; each next one pushes the last one out
    $('pscene').innerHTML = `
      <div class="card dcard" id="s1"><div class="eb">Your script</div>
        <div class="h" style="font-size:72px;margin-top:12px"><span id="five">Five lines</span></div>
        <div class="src mono" style="margin:6px 0 18px">projects/starter/project.json</div>
        ${['Your repo can make its own reels.', 'Just write five lines about your product.', 'Repo2Reels speaks them, scores the music…', 'No API keys. No GPU.', 'Repo2Reels. Free and open source.']
          .map((s, i) => `<div class="sl" id="l${i}"><span class="n">${i + 1}</span><span class="x">${s}</span></div>`).join('')}</div>
      <div class="card dcard" id="s2"><div class="eb">One command</div>
        <div class="h" style="font-size:72px;margin:12px 0 10px">make.py</div>
        ${[['Speaks every line', 'A Kokoro voice, on your computer'], ['Scores the music', 'Pad, bass and drums in one key'], ['Cuts on the beat', 'Every scene lands on a 120 bpm grid']]
          .map(([a, b], i) => `<div class="stp" id="st${i}"><div class="ic" id="ic${i}">${I_CHECK}</div><div><div class="t">${a}</div><div class="s">${b}</div></div></div>`).join('')}
        <div class="beats" id="beats">${'<div class="bt"></div>'.repeat(8)}</div></div>
      <div class="card dcard" id="s3"><div class="eb">What it needs</div>
        <div class="h" style="font-size:72px;margin:12px 0 4px">Just your computer</div>
        <div class="tile" id="t0">${I_NOKEY}<div class="t">No API keys</div></div>
        <div class="tile" id="t1">${I_NOGPU}<div class="t">No GPU</div></div>
        <div class="tile gold" id="t2">${I_LAPTOP}<div class="t"><span id="own">Your own computer</span></div></div></div>`;
    this.cards = [{ id: 's1', at: this.paperAt + .1 }, { id: 's2', at: LN(3).on - .1 }, { id: 's3', at: LN(4).on - .1 }];
    deckSetup(this.cards);

    // card 1: the five lines print in while line 2 is said, and the card grows with them
    const a = wt(2, 'Write'), b = we(2, 'product');
    this.lt = [0, 1, 2, 3, 4].map(i => a + i * (b - a) / 5);
    this.lt.forEach(x => ev(x, 'tick'));
    this.rv1 = revealSetup($('s1'), this.lt.map((x, i) => ['l' + i, x]));
    this.c5 = RN.circle($('five'), { seed: 8, pad: 12 }); this.t5 = wt(2, 'five'); ev(this.t5, 'scribble');

    // card 2: each step is ticked on its word; the beat strip starts on "beat"
    this.st = [wt(3, 'speaks'), wt(3, 'scores'), wt(3, 'cuts')]; this.st.forEach(x => ev(x, 'pop'));
    this.tb = wt(3, 'beat');

    // card 3: one tile per thing it doesn't need, then the computer, highlighted
    this.tt = [wt(4, 'keys'), wt(4, 'GPU'), wt(4, 'computer')]; this.tt.forEach(x => ev(x, 'pop'));
    this.rv3 = revealSetup($('s3'), this.tt.map((x, i) => ['t' + i, x]));
    this.hown = RN.highlight($('own'), { seed: 21 }); this.town = we(4, 'computer'); ev(this.town, 'scribble');

    this.posterAt = Math.min(this.tc + .5, this.paperAt - .2);   // the cover: the hook circled, the file made
  },
  scene(t) {
    hookIn(this.hw, t); nightCard($('term'), t, .25);
    typeIn($('cmd'), 'python3 make.py projects/starter', t, ...this.ty, this.tmade);
    enter($('made'), t, this.tmade, { dy: 14, s0: .9 });
    this.circ.set(p(t, this.tc, this.tc + .45));

    deck(t, this.cards);
    reveal($('s1'), this.rv1, t);
    this.lt.forEach((x, i) => enter($('l' + i), t, x, { dy: 12, s0: 1 }));
    this.c5.set(p(t, this.t5, this.t5 + .45));

    this.st.forEach((x, i) => {
      $('st' + i).style.opacity = t >= x ? 1 : .35;                    // waiting steps show dimmed, never missing
      enter($('ic' + i), t, x, { dy: 0, s0: .4, cfg: { damping: 11, stiffness: 240 } });
    });
    const beat = Math.floor((t + .02) / .5);                           // the music's beat: two a second
    [...$('beats').children].forEach((el, i) => {
      const on = t >= this.tb && beat % 8 === i;
      el.className = 'bt' + (on ? ' on' : '');
      el.style.scale = `1 ${on ? 1 - .5 * p(t, beat * .5, beat * .5 + .45) : .5}`;
    });

    reveal($('s3'), this.rv3, t);
    this.tt.forEach((x, i) => enter($('t' + i), t, x, { dy: 20, s0: .92, cfg: { damping: 13, stiffness: 220 } }));
    this.hown.set(p(t, this.town, this.town + .45));
  },
};
