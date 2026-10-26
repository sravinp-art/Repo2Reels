// Keyva example: ten reels (batch 3). Each REELS entry is one reel: the corner bug, the end-card label and
// footnote, setup() (build the DOM, read word times, queue sound cues) and scene(t) (pose everything at time t).
// Helpers (enter, deck, RN.*, wt/we, ev ...) live in engine/engine.html; see docs/writing-scenes.md.

// ---------------------------------------------------------------- icons used by these scenes
const OKI = `<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#2e6b34" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>`;
const ICON_S = `<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>`;
// ================================================================== R11  the names on record
REELS.r11 = {
  bug: 'Every area', label: 'Search areas by the name you know',
  foot: 'Dubai’s rent records file communities under their official sector names; Downtown Dubai is filed under the area name Burj Khalifa. Dubai Land Department records.',
  setup() {
    std(this, 7);
    hookSetup(this, ['There’s no <g>JVC</g>', 'in Dubai’s', 'rent records.'], { max: 170, top: 290, extra: `
      <div class="glass ncard" id="ns" style="top:930px"><div class="tag">Illustrative</div><div class="eb">Rent records · search areas</div>
        <div class="in mono" id="q" style="margin-top:22px"></div>
        <div id="nores" style="margin-top:22px;font:600 34px InterK;color:#f3b49a;opacity:0">0 areas named “JVC”</div></div>` });
    const C = [['JVC', ['Al Barsha', 'South Fourth'], 'In the rent records'], ['Dubai Marina', ['Marsa Dubai'], 'In the rent records'],
      ['JLT', ['Al Thanyah', 'Fifth'], 'In the rent records'], ['Dubai Hills', ['Hadaeq Sheikh', 'Mohammed Bin Rashid'], 'In the rent records'], ['Downtown', ['Burj Khalifa'], 'The area name on record']];
    $('pscene').innerHTML = C.map((c, i) => `<div class="qcard" id="qc${i}"><div class="face front"><div class="eb">What people call it</div><div class="num">${i + 1} / 5</div>
        <div class="nm" style="font-size:${fitSize(c[0], 'Sora', 600, 740, 190, 80, -.035)}px">${c[0]}</div><div class="sub">Search it the way you say it</div></div>
      <div class="face back"><div class="eb">How it’s filed</div><div class="num">${i + 1} / 5</div>
        ${c[1].map(l => `<div class="nm" style="font-size:${Math.min(118, fitSize(c[1].reduce((a, b) => a.length > b.length ? a : b), 'Sora', 600, 740, 118, 56, -.035))}px">${l}</div>`).join('')}
        <div class="sub">${c[2]} · Dubai Land Department</div></div></div>`).join('');
    const at = [this.paperAt + .1, LN(3).on - .1, LN(4).on - .1, LN(5).on - .1, LN(6).on - .1];
    this.cards = at.map((a, i) => ({ id: 'qc' + i, at: a })); deckSetup(this.cards);
    this.flip = [wt(2, 'as'), wt(3, 'Marsa') - .12, wt(4, 'Al') - .12, wt(5, 'Hadaeq') - .12, wt(6, 'Burj') - .12];
    this.flip.forEach(x => ev(x, 'flip'));
    this.qa = [.55, .95]; typeEventsK('JVC', ...this.qa); this.tno = wt(1, 'rent'); ev(this.tno, 'strike');
    this.circ = RN.circle(this.hw[2], { seed: 4, pad: 14, width: 7 }); this.tc = we(1, 'JVC') + .05; ev(this.tc, 'scribble');
    this.posterAt = this.tno + .45;   // cover frame
  },
  scene(t) {
    hookIn(this.hw, t); this.circ.set(p(t, this.tc, this.tc + .45));
    nightCard($('ns'), t, .2); typeIn($('q'), 'JVC', t, ...this.qa, this.tno);
    enter($('nores'), t, this.tno, { dy: 14, s0: .9 });
    deck(t, this.cards);
    this.cards.forEach((c, i) => { const k = flipCard($('qc' + i), t, this.flip[i], .5); $('qc' + i).style.scale = String(1 + .04 * Math.sin(Math.PI * k)); });
  },
};

// ================================================================== R12  India: the LRS limit
REELS.r12 = {
  bug: 'Buying from India', label: 'Buying from India: every rule, with its source',
  foot: 'Reserve Bank of India, Liberalised Remittance Scheme; Income-tax Act 2025, s.394(1). Read 25 Sep 2026. NRIs: the scheme doesn’t apply. General information, not tax advice.',
  setup() {
    std(this, 5);
    hookSetup(this, ['Buying from India?', 'You can send', '<g>USD 250,000</g> a year.'], { max: 150, top: 290, extra: `
      <div class="glass ncard" id="nm" style="top:960px"><div class="eb">Liberalised Remittance Scheme</div>
        <div class="row" style="margin-top:18px"><span style="font-size:28px;color:rgba(255,255,255,.75)">Per person, per financial year</span><span class="mono" id="nmv" style="font-size:40px;font-weight:700;color:var(--goldlight)">USD 0</span></div>
        <div class="bar" style="margin-top:18px"><div class="fill" id="nmf" style="width:100%;background:linear-gradient(90deg,#12776c,#f0c579)"></div></div>
        <div class="stamp" id="nmst" style="right:40px;top:-30px;color:#f0c579;background:rgba(2,22,20,.85)">LIMIT</div></div>` });
    $('pscene').innerHTML = `
      <div class="card dcard" id="s1"><div class="eb">Per resident · per financial year</div>
        <div class="big" id="s1v" style="color:var(--teal);margin-top:26px;font-size:110px">USD 250,000</div>
        <div class="note" style="margin-top:22px">April to March, <span id="comb" style="font-weight:600">all purposes combined</span></div>
        <div class="chip tint" id="s1c" style="margin-top:26px">Buying property abroad is a named use</div></div>
      <div class="card dcard" id="s2"><div class="eb">Co-owners on the title</div>
        <div class="row" style="margin-top:34px;padding:0 10px">${[1, 2, 3, 4].map(i => `<div class="ava" id="av${i}">${i}<span class="c">USD 250k</span></div>`).join('')}</div>
        <div class="note" style="margin-top:64px">Each sends their own. Together:</div><div class="big" id="s2v" style="font-size:92px;white-space:nowrap;color:var(--teal);margin-top:10px;align-self:flex-start">USD 1,000,000</div>
        <div class="src" id="s2n" style="margin-top:14px">Only co-owners: the Reserve Bank doesn’t allow clubbing for family members who aren’t on the title.</div></div>
      <div class="card dcard" id="s3"><div class="eb">Tax collected at source (TCS)</div>
        <div class="big" style="font-size:170px;color:var(--rust);margin-top:14px">20%</div><div class="note" style="margin-top:8px">on remittances past <b>₹10 lakh</b></div>
        <div class="note" style="margin-top:26px"><span id="nc" style="font-weight:600">Not a cost of the property:</span> it’s credited against your income tax, or refunded when you file.</div>
        <div class="src" style="margin-top:20px">Whether it applies to the whole amount or only the part above ₹10 lakh: ask your bank in writing.</div></div>`;
    this.cards = [{ id: 's1', at: this.paperAt + .1 }, { id: 's2', at: LN(3).on - .1 }, { id: 's3', at: LN(4).on - .1 }]; deckSetup(this.cards);
    this.tl = wt(1, 'limit'); ev(this.tl, 'stamp'); ev(.5, 'rise');
    this.ucomb = RN.underline($('comb'), { seed: 6 }); this.tcomb = wt(2, 'combined'); ev(this.tcomb, 'scribble');
    this.tco = wt(3, 'co-owners'); this.tm = wt(3, 'million'); ev(this.tm, 'chime');
    for (let i = 0; i < 4; i++) ev(this.tco + .25 + i * .18, 'pop');
    this.c2 = RN.circle($('s2v'), { seed: 12, pad: 16 });
    this.tnc = wt(4, 'not'); this.hnc = RN.highlight($('nc'), { seed: 13 }); ev(wt(4, 'twenty'), 'hit'); ev(this.tnc, 'scribble');
    this.posterAt = this.tl + .45;   // cover frame
  },
  scene(t) {
    hookIn(this.hw, t); nightCard($('nm'), t, .3);
    const k = SMOOTH(p(t, .5, this.tl)); $('nmf').style.scale = `${k} 1`; $('nmv').textContent = 'USD ' + fmt(250000 * k);
    stamp($('nmst'), t, this.tl, 6);
    deck(t, this.cards);
    $('s1v').style.scale = String(pscale(spr(t - this.paperAt - .2, { damping: 12, stiffness: 160 }), .8, 1));
    this.ucomb.set(p(t, this.tcomb, this.tcomb + .45));
    for (let i = 1; i <= 4; i++) enter($('av' + i), t, this.tco + .25 + (i - 1) * .18, { dy: 30, s0: .7, cfg: { damping: 12, stiffness: 200 } });
    $('s2v').textContent = 'USD ' + fmt(Math.round(counter(t, this.tco + .3, this.tm - this.tco - .3, 0, 1000)) * 1000);
    $('s2v').style.opacity = t >= this.tco + .34 ? 1 : 0;   // appears with its count, never as "USD 0"
    this.c2.set(p(t, this.tm, this.tm + .5));
    this.hnc.set(p(t, this.tnc, this.tnc + .45));
  },
};

// ================================================================== R13  the knowledge fee
const R13L = [['Knowledge fee', 10], ['Innovation fee', 10], ['Title deed certificate', 250], ['Map fee, villas and apartments', 250], ['Title deed', 250], ['Knowledge fee', 10], ['Innovation fee', 10]];
REELS.r13 = {
  bug: 'Every fee, who sets it', label: 'Every fee, and who sets it',
  foot: 'Also payable, and on Keyva’s fee list: the 4% transfer fee, trustee office registration, mortgage registration, bank valuation and agency commission. Small fees: Dubai Land Department service pages, read 25 Sep 2026; map fee shown for villas and apartments.',
  setup() {
    std(this, 5); this.endAt = wt(5, 'Keyva') - .1;
    hookSetup(this, ['Yes, Dubai has a', '<g>knowledge</g> <g>fee.</g>'], { max: 170, top: 300, extra: `
      <div class="glass ncard" id="nr" style="top:900px"><div class="eb">Registration fees · receipt</div>
        <div class="row" style="margin-top:18px;font-size:32px"><span>Title deed certificate</span><span class="mono">AED 250</span></div>
        <div class="row" style="margin-top:16px;font-size:32px"><span id="nkf">Knowledge fee</span><span class="mono">AED 10</span></div>
        <div class="row" style="margin-top:16px;font-size:32px"><span>Innovation fee</span><span class="mono">AED 10</span></div></div>` });
    $('pscene').innerHTML = `<div class="card dcard rcpt" id="rc"><div class="eb">Sale registration · published fees</div>
        ${R13L.slice(0, 4).map((l, i) => `<div class="rl" id="rl${i}"><span class="l">${l[0]}</span><span class="a">AED ${l[1]}</span></div>`).join('')}
        <div class="rh" id="rh">With a mortgage, again <span class="chip gold" id="x2" style="font-size:24px;padding:6px 14px;margin-left:10px;opacity:0">×2</span></div>
        ${R13L.slice(4).map((l, i) => `<div class="rl" id="rl${i + 4}"><span class="l">${l[0]}</span><span class="a">AED ${l[1]}</span></div>`).join('')}
        <div class="row" id="rtot" style="margin-top:22px;opacity:0"><span class="lbl">These small fees</span><span class="big" id="rtv" style="font-size:72px;color:var(--teal)">AED 0</span></div></div>`;
    this.tkf = .9; this.ckf = RN.circle($('nkf'), { seed: 21, pad: 14 }); ev(this.tkf + .1, 'scribble');
    this.tl = [wt(2, 'ten'), wt(2, 'innovation'), wt(3, 'title'), wt(3, 'map'), wt(4, 'title'), wt(4, 'knowledge'), wt(4, 'innovation')];
    this.tl.forEach(x => ev(x, 'print')); this.trh = LN(4).on; this.tx2 = wt(4, 'twice'); ev(this.tx2, 'stamp');
    this.ttot = LN(5).on; ev(this.ttot + .1, 'chime');
    this.rv = revealSetup($('rc'), [['rl0', this.tl[0]], ['rl1', this.tl[1]], ['rl2', this.tl[2]], ['rl3', this.tl[3]], ['rh', this.trh], ['rl4', this.tl[4]], ['rl5', this.tl[5]], ['rl6', this.tl[6]], ['rtot', this.ttot]]);
    this.posterAt = this.tkf + .7;   // cover frame
  },
  scene(t) {
    hookIn(this.hw, t); nightCard($('nr'), t, .25); this.ckf.set(p(t, this.tkf, this.tkf + .5));
    enter($('rc'), t, this.paperAt + .1); reveal($('rc'), this.rv, t);
    this.tl.forEach((x, i) => { const el = $('rl' + i); const k = EO(p(t, x - .05, x + .25)); el.style.opacity = k; el.style.translate = `${(1 - k) * -30}px 0`; el.style.background = t >= x && t < x + .55 ? 'var(--goldsoft)' : 'transparent'; });
    enter($('rh'), t, this.trh, { dy: 12, s0: 1 }); stamp($('x2'), t, this.tx2, -6); $('x2').style.position = 'relative';
    // the payoff total lands fast so it holds on screen before the end card (it was counting until 0.35 s before)
    enter($('rtot'), t, this.ttot, { dy: 16, s0: 1 }); $('rtv').textContent = 'AED ' + fmt(counter(t, this.ttot + .05, .55, 0, 790));
  },
};

// ================================================================== R14  sometimes it says no
REELS.r14 = {
  bug: 'Check an asking price', label: 'Prices with their count and dates',
  foot: 'The listing check needs 8 comparable completed-home sales. An area’s current price uses its last 30 days, with at least 5 sales. Dubai Marina figures: Dubai Land Department records.',
  setup() {
    std(this, 4); this.endAt = we(4, 'figure') + .35;
    hookSetup(this, ['Most price tools', 'always give a number.', 'Keyva sometimes <g>won’t.</g>'], { max: 130, top: 300, extra: `
      <div class="glass ncard" id="np" style="top:930px;padding-bottom:86px"><div class="tag" style="top:auto;bottom:28px">Illustrative</div><div class="eb">Fair price</div>
        <div class="big mono" id="npv" style="margin-top:18px;color:#fff">AED 1,000</div><div class="sub" style="margin-top:12px;font-size:28px;color:rgba(255,255,255,.7)">per sq ft, from … how many sales?</div>
        <div class="stamp" id="npst" style="right:36px;top:60px;color:#f3b49a;background:rgba(2,22,20,.85)">NOT ENOUGH SALES</div></div>` });
    $('pscene').innerHTML = `
      <div class="card dcard" id="s1"><div class="tag">Illustrative</div><div class="eb">The price</div>
        <div class="lbl" style="margin-top:26px">Comparable sales found</div><div class="dots">${Array.from({ length: 8 }, (_, i) => `<div class="dot" id="d${i}"></div>`).join('')}</div>
        <div class="note" style="margin-top:30px;font-size:32px">Fewer than 8 recorded sales match a home this size here, so any “fair price” we showed would be <span id="gw" style="font-weight:600">guesswork.</span></div></div>
      <div class="card dcard" id="s2"><div class="eb">Dubai Marina · October 2026</div>
        <div class="h" style="font-size:52px;margin-top:16px">“This month”, on 2 October</div>
        <div class="days">${Array.from({ length: 24 }, (_, i) => `<div class="day${i < 2 ? ' on' : ''}" id="dy${i}">${i + 1}</div>`).join('')}</div>
        <div class="row" style="margin-top:24px;align-items:baseline"><span class="note" id="twod" style="font-weight:600">2 days of sales</span><span class="big" id="s2v" style="font-size:96px;color:var(--teal)">0</span></div>
        <div class="src" id="rs2" style="text-align:right">recorded sales</div></div>
      <div class="card dcard" id="s3"><div class="eb">How Keyva prices an area</div>
        <div style="position:relative;height:40px;margin-top:24px"><span style="position:absolute;left:77%;translate:-50% 0;white-space:nowrap;font:600 28px InterK;color:var(--teal)">Last 30 days</span></div>
        <div class="bar" style="margin-top:8px;height:64px"><div class="fill" id="win" style="left:auto;right:0;width:46%;background:rgba(11,79,74,.18);border:3px solid var(--teal)"></div></div>
        <div style="position:relative;height:36px;margin-top:10px"><span class="src" style="position:absolute;left:0">Earlier</span><span class="src" style="position:absolute;left:54%">3 Sep</span><span class="src" style="position:absolute;right:0">2 Oct</span></div>
        <div class="chip tint" id="flr" style="margin-top:14px;align-self:flex-start;font-size:27px">At least 5 sales in the window</div>
        <div style="margin-top:30px;padding:26px 28px;border-radius:24px;background:var(--tint)"><div class="lbl" style="color:var(--teal)">Every figure shows its count</div>
          <div class="src" style="margin-top:6px">Example: Dubai Marina, ready homes, typical price</div>
          <div class="big" style="font-size:76px;color:var(--teal);margin-top:10px">AED 2,005<span style="font:500 30px InterK;color:var(--muted)"> /sq ft</span></div>
          <div class="note" style="margin-top:12px"><span id="cnt" style="font-weight:600">2,690 sales</span> · <span id="dts">12 months to 2 Oct 2026</span></div></div></div>`;
    this.cards = [{ id: 's1', at: this.paperAt + .1 }, { id: 's2', at: LN(3).on - .1 }, { id: 's3', at: LN(4).on - .1 }]; deckSetup(this.cards);
    this.tst = wt(1, "won't"); ev(this.tst, 'stamp');
    this.tdots = wt(2, 'eight'); for (let i = 0; i < 5; i++) ev(this.tdots + i * .14, 'tick');
    this.tgw = wt(2, 'guesswork'); this.hgw = RN.highlight($('gw'), { seed: 31 }); ev(this.tgw, 'scribble');
    this.tdays = wt(3, 'two'); { const a = $('dy0'), b = $('dy1'); const box = document.createElement('div'); box.style.cssText = `position:absolute;left:${a.offsetLeft}px;top:${a.offsetTop}px;width:${b.offsetLeft + b.offsetWidth - a.offsetLeft}px;height:${a.offsetHeight}px`; a.offsetParent.appendChild(box); this.c2d = RN.circle(box, { seed: 32, pad: 12 }); } this.t22 = wt(3, 'twenty-two'); ev(this.t22, 'chime');
    this.twin = wt(4, 'thirty'); ev(this.twin, 'rise'); this.tcnt = wt(4, 'count'); ev(this.tcnt, 'scribble');
    this.ucnt = RN.underline($('cnt'), { seed: 33 }); this.udts = RN.underline($('dts'), { seed: 34 });
    this.posterAt = this.tst + .45;   // cover frame
  },
  scene(t) {
    hookIn(this.hw, t); nightCard($('np'), t, .25);
    const r = rng(Math.floor(t * 12)); $('npv').textContent = t < this.tst ? 'AED ' + fmt(900 + r() * 2400) : 'AED ????';
    stamp($('npst'), t, this.tst, -7);
    deck(t, this.cards);
    for (let i = 0; i < 8; i++) { const on = i < 5 && t >= this.tdots + i * .14; $('d' + i).className = 'dot' + (on ? ' f' : ''); $('d' + i).style.scale = on ? String(pscale(spr(t - this.tdots - i * .14, { damping: 11, stiffness: 230 }), .5, 1)) : '1'; }
    this.hgw.set(p(t, this.tgw, this.tgw + .45));
    this.c2d.set(p(t, this.tdays, this.tdays + .5)); $('s2v').textContent = fmt(counter(t, this.t22 - .3, .6, 0, 22));
    $('s2v').style.opacity = $('rs2').style.opacity = t >= this.t22 - .27 ? 1 : 0;   // never "0 recorded sales" while the voice is still on the two days
    $('win').style.scale = `${SMOOTH(p(t, this.twin, this.twin + .8))} 1`; enter($('flr'), t, this.twin + .45, { dy: 12, s0: .9 });
    this.ucnt.set(p(t, this.tcnt, this.tcnt + .4)); this.udts.set(p(t, this.tcnt + .3, this.tcnt + .75));
  },
};

// ================================================================== R15  off-plan escrow
REELS.r15 = {
  bug: 'Check an off-plan project', label: 'Check an off-plan project',
  foot: 'Dubai Law No. (8) of 2007 on real estate escrow accounts. Illustrative result, names blurred. Keyva shows what the register holds and says what it can’t check. Not legal advice.',
  setup() {
    std(this, 4); this.endAt = we(4, 'you') + .35;
    hookSetup(this, ['Off-plan?', 'Don’t pay the', 'developer <g>directly.</g>'], { max: 170, top: 290, extra: `
      <div class="glass ncard" id="nt" style="top:960px"><div class="tag">Illustrative</div><div class="eb">Bank transfer</div>
        <div class="row" style="margin-top:22px;font-size:34px"><span style="color:rgba(255,255,255,.7)">To</span><span id="ntdev" style="font-weight:600">Developer’s own account</span></div>
        <div class="chip gold" id="ntes" style="margin-top:22px;font-size:30px;background:rgba(240,197,121,.18);color:var(--goldlight)">To the project’s escrow account</div></div>` });
    $('pscene').innerHTML = `
      <div class="card dcard" id="s1"><div class="eb">By law · Dubai Law No. 8 of 2007</div>
        <div class="flow"><div class="node">Your payments</div><div class="arrow">→</div><div class="node gold" id="vault">Project escrow account</div><div class="arrow">→</div><div class="node">Building the project</div></div>
        <div style="display:flex;flex-direction:column;gap:16px;margin-top:30px;align-items:flex-start">
          <div class="chip tint" id="e1">One account per project</div><div class="chip tint" id="e2">Used only to build it</div><div class="chip ok" id="e3">Protected from the developer’s creditors</div></div></div>
      <div class="card dcard" id="s2"><div class="tag">Illustrative result</div><div class="eb">Check an off-plan project</div>
        <div class="crow" id="c1" style="margin-top:14px"><div class="k">Is it on the register?</div><div class="vv">Yes · project no. <span class="blur">4821</span></div></div>
        <div class="crow" id="c2"><div class="k">Status per the register</div><div class="vv"><span class="blur">Under construction</span> · Target completion: <span class="blur">Mar 2028</span></div></div>
        <div class="crow" id="c3"><div class="k">Escrow</div><div class="vv">Escrow bank on the register: <span class="blur">Gulf Bank PJSC</span></div></div>
        <div class="crow" id="c4"><div class="k">Registered developer</div><div class="vv"><span class="blur">Harbour Homes LLC</span> · Licence to 20<span class="blur">29</span></div></div>
        <div class="crow" id="c5" style="background:var(--goldsoft);border-radius:20px;padding:18px 22px;margin-top:10px"><div class="k" style="color:var(--goldtxt)">What we cannot check</div>
          <div class="vv" style="font-size:29px"><span id="fund">Whether the escrow account is funded.</span><br>The escrow account number (not stored).</div></div></div>`;
    this.cards = [{ id: 's1', at: this.paperAt + .1 }, { id: 's2', at: LN(3).on - .1 }]; deckSetup(this.cards);
    this.tx = wt(1, 'directly'); this.xdev = RN.cross($('ntdev'), { seed: 41, pad: 8 }); ev(this.tx, 'strike'); ev(this.tx + .5, 'pop');
    this.te = [wt(2, 'every'), wt(2, 'only'), wt(2, 'protected')]; this.te.forEach(x => ev(x, 'pop')); this.tv = wt(2, 'escrow'); ev(this.tv, 'chime');
    this.cv = RN.circle($('vault'), { seed: 42, pad: 12 });
    this.tc = [LN(3).on + .3, wt(3, 'status'), wt(3, 'escrow'), wt(3, 'licence'), LN(4).on]; this.tc.forEach(x => ev(x, 'tick'));
    this.rv = revealSetup($('s2'), this.tc.map((x, i) => ['c' + (i + 1), x]));   // before any annotation on the card: it changes the layout
    this.tf = wt(4, 'funded'); this.hf = RN.highlight($('fund'), { seed: 43 }); ev(this.tf, 'scribble');
    this.posterAt = this.tx + 1.0;   // cover frame
  },
  scene(t) {
    hookIn(this.hw, t); nightCard($('nt'), t, .25); this.xdev.set(p(t, this.tx, this.tx + .45)); enter($('ntes'), t, this.tx + .5, { dy: 20, s0: .85 });
    deck(t, this.cards);
    this.cv.set(p(t, this.tv, this.tv + .5)); chips(t, [['e1', this.te[0]], ['e2', this.te[1]], ['e3', this.te[2]]]);
    this.tc.forEach((x, i) => enter($('c' + (i + 1)), t, x, { dy: 16, s0: 1 })); reveal($('s2'), this.rv, t);
    this.hf.set(p(t, this.tf, this.tf + .45));
  },
};

// ================================================================== R16  ninety days' notice
REELS.r16 = {
  bug: 'Rent increase check', label: 'Is this rent rise lawful?',
  foot: 'A guide, not a ruling. Bands: Decree No. 43 of 2013. RERA’s calculator is the authoritative instrument and the Rental Dispute Centre decides disputes. Illustrative dates.',
  setup() {
    std(this, 4); this.endAt = we(4, 'side', 1) + .35;
    hookSetup(this, ['Rent going up?', 'Check the date', 'on the <g>notice.</g>'], { max: 170, top: 290, extra: `
      <div class="glass ncard" id="nl" style="top:960px"><div class="tag">Illustrative</div><div class="eb">Notice of rent increase</div>
        <div style="margin-top:20px;font-size:32px;line-height:1.4;color:rgba(255,255,255,.85)">Your rent will rise at renewal on <b>1 May</b>.</div>
        <div style="margin-top:16px;font:600 32px InterK;color:#fff">Dated: <span id="ndt" class="mono">14 March</span></div></div>` });
    const X = d => 40 + d / 120 * 660;   // day index from 1 Jan, inside the card
    $('pscene').innerHTML = `
      <div class="card dcard" id="s1"><div class="tag">Illustrative dates</div><div class="eb">Before changing any term</div>
        <div class="row" style="margin-top:14px;align-items:baseline"><span class="big" id="n90" style="font-size:150px;color:var(--teal)">0</span><span class="note" style="width:420px;text-align:right">days’ written notice, <span id="tm" style="font-weight:600">rent included</span></span></div>
        <div class="tl"><div class="axis"></div>
          <div class="win" id="win" style="left:${X(30)}px;width:${X(120) - X(30)}px"></div><div class="wl" id="wl" style="left:${(X(30) + X(120)) / 2}px">90 days</div>
          <div class="mk" style="left:${X(120)}px;background:var(--teal)"></div><div class="ml" style="left:${X(120)}px;color:var(--teal);transform:translateX(calc(-50% - 52px))">Renewal · 1 May</div>
          <div class="mk" id="lmk" style="left:${X(72)}px;background:var(--rust);opacity:0"></div><div class="ml" id="lml" style="left:${X(72)}px;color:var(--rust);opacity:0">Notice · 14 Mar</div>
          <div class="ml" style="left:${X(30)}px;color:var(--muted)">31 Jan</div>
          <div class="stamp" id="late" style="left:10px;top:30px;color:var(--rust);background:#fff">SERVED LATE</div></div>
        <div class="note" id="bind" style="margin-top:6px;opacity:0">An otherwise lawful increase <span id="nb" style="font-weight:600">doesn’t bind you</span> for that renewal.</div></div>
      <div class="card dcard" id="s2"><div class="eb">Keyva’s rent check</div>
        <div class="cols" id="cols2" style="grid-template-columns:1.15fr 1fr">
          <div class="col" id="cA" style="border-style:solid;border-color:var(--line)"><div class="ch" style="color:var(--teal)">Legal cap</div>
            ${[['Up to 10% below', 'None'], ['10–20%', '5%'], ['20–30%', '10%'], ['30–40%', '15%'], ['Over 40%', '20%']].map(r => `<div class="row" style="font-size:25px;padding:7px 0;border-bottom:1.5px solid var(--line)"><span>${r[0]}</span><b>${r[1]}</b></div>`).join('')}
            <div class="src" style="margin-top:8px">by how far below market you pay</div></div>
          <div class="col" id="cB" style="border-style:solid;border-color:var(--gold);background:var(--goldsoft)"><div class="ch" style="color:var(--goldtxt)">Notice</div>
            <div class="big" style="font-size:96px;color:var(--goldtxt)">90</div><div class="note" style="margin-top:10px">days’ written notice before changing any term</div></div></div></div>`;
    this.cards = [{ id: 's1', at: this.paperAt + .1 }, { id: 's2', at: LN(4).on - .1 }]; deckSetup(this.cards);
    this.tdt = wt(1, 'date'); this.cdt = RN.circle($('ndt'), { seed: 51, pad: 12 }); ev(this.tdt, 'scribble');
    this.t90 = wt(2, 'ninety'); ev(this.t90, 'rise'); this.ttm = wt(2, 'rent'); this.utm = RN.underline($('tm'), { seed: 52 });
    this.tlate = LN(3).on; ev(this.tlate + .35, 'stamp'); this.tb = wt(3, 'bind'); this.ub = RN.underline($('nb'), { seed: 53, color: '#a84720' });
    this.tA = wt(4, 'cap'); this.tB = wt(4, 'notice'); ev(this.tA, 'pop'); ev(this.tB, 'pop');
    this.rv = revealSetup($('s2'), [['cols2', this.tA - .1]]);
    this.posterAt = this.tdt + .6;   // cover frame
  },
  scene(t) {
    hookIn(this.hw, t); nightCard($('nl'), t, .25); this.cdt.set(p(t, this.tdt, this.tdt + .5));
    deck(t, this.cards);
    $('n90').textContent = fmt(counter(t, this.t90 - .2, .7, 0, 90)); $('win').style.scale = `${SMOOTH(p(t, this.t90 - .2, this.t90 + .7))} 1`;
    $('n90').style.opacity = t >= this.t90 - .17 ? 1 : 0;   // never "0 days' written notice" on screen before the count
    this.utm.set(p(t, this.ttm, this.ttm + .4));
    enter($('lmk'), t, this.tlate, { dy: -60, s0: 1 }); enter($('lml'), t, this.tlate + .1, { dy: -20, s0: 1 });
    stamp($('late'), t, this.tlate + .35, -6); enter($('bind'), t, this.tlate + .5, { dy: 12, s0: 1 }); this.ub.set(p(t, this.tb, this.tb + .4));
    enter($('cA'), t, this.tA - .1, { dy: 24, s0: .95 }); enter($('cB'), t, this.tB - .1, { dy: 24, s0: .95 }); reveal($('s2'), this.rv, t);
  },
};

// ================================================================== R17  the car loan
REELS.r17 = {
  bug: 'What a bank may lend', label: 'What a bank may lend',
  foot: 'Illustrative income and loans. Keyva’s mortgage calculator applies a 50% debt-burden cap from the Central Bank’s published caps; banks can be stricter. Not financial advice.',
  setup() {
    std(this, 5); this.endAt = we(5, 'caps') + .35;
    hookSetup(this, ['That car loan', 'could <g>shrink</g> your', 'mortgage.'], { max: 170, top: 290, extra: `
      <div class="glass ncard" id="nc" style="top:960px"><div class="tag">Illustrative</div><div class="eb">Monthly repayments</div>
        <div class="row" style="margin-top:20px;font-size:32px"><span>Car loan</span><span class="mono" style="color:#f3b49a">AED 3,000</span></div>
        <div class="lbl" style="margin-top:22px;color:rgba(255,255,255,.7)">Room left for a mortgage</div>
        <div class="bar" style="margin-top:12px"><div class="fill" id="ncf" style="width:100%;background:var(--goldlight)"></div></div></div>` });
    $('pscene').innerHTML = `
      <div class="card dcard" id="s1"><div class="eb">The Central Bank’s debt-burden cap</div>
        <div class="row" style="margin-top:14px;align-items:baseline"><span class="big" style="font-size:160px;color:var(--teal)">50%</span><span class="note" style="width:380px;text-align:right">of your income, <span id="tog" style="font-weight:600">all loans together</span></span></div>
        <div class="lbl" style="margin-top:24px">Monthly income</div><div class="stack" id="inc"><div class="seg" id="half" style="left:0;width:50%;background:var(--teal)">Repayments, at most</div></div></div>
      <div class="card dcard" id="s2"><div class="tag">Illustrative</div><div class="eb">Earn AED 30,000 a month</div>
        <div class="kv" style="margin-top:20px"><span>Monthly income</span><span class="v" id="v1">AED 0</span></div>
        <div class="kv"><span>Cap for every loan you have</span><span class="v" id="v2" style="color:var(--teal)">AED 0</span></div>
        <div class="lbl" style="margin-top:30px">Inside the cap</div>
        <div class="stack" style="height:110px"><div class="seg" id="car" style="left:0;width:20%;background:var(--rust)">Car 3k</div><div class="seg" id="mort" style="left:20%;width:80%;background:var(--teal)">Mortgage room AED 12,000</div></div>
        <div class="row" style="margin-top:24px"><span class="chip warn" id="m20">A fifth less to borrow against</span><span class="src">same rate and term</span></div></div>
      <div class="card dcard" id="s3"><div class="eb">Keyva’s mortgage calculator</div>
        <div class="fl" style="margin-top:22px">Monthly income (AED)</div><div class="in mono">30,000</div>
        <div class="fl" style="margin-top:20px">Existing monthly debts (AED, optional)</div><div class="in mono" id="dbt"></div>
        <div class="row" style="margin-top:28px;padding:22px 26px;border-radius:22px;background:var(--tint)"><span class="lbl" style="color:var(--teal)">DBR utilization</span><span style="font:600 26px InterK;color:var(--muted)">cap: 50%</span></div></div>`;
    this.cards = [{ id: 's1', at: this.paperAt + .1 }, { id: 's2', at: LN(3).on - .1 }, { id: 's3', at: LN(5).on - .1 }]; deckSetup(this.cards);
    this.tsh = wt(1, 'shrink'); ev(this.tsh, 'hit');
    this.thalf = wt(2, 'half'); ev(this.thalf, 'rise'); this.ttog = wt(2, 'together'); this.utog = RN.underline($('tog'), { seed: 61 });
    this.t30 = wt(3, 'thirty'); this.t15 = wt(3, 'fifteen'); ev(this.t15, 'chime');
    this.tcar = wt(4, 'car'); this.t12 = wt(4, 'twelve'); this.t5 = wt(4, 'fifth'); ev(this.tcar, 'pop'); ev(this.t12, 'pop'); ev(this.t5, 'hit');
    this.tdb = wt(5, 'existing'); this.tdb2 = [this.tdb - .1, this.tdb + .35]; typeEventsK('3,000', ...this.tdb2);
    this.posterAt = this.tsh + .9;   // cover frame
  },
  scene(t) {
    hookIn(this.hw, t); nightCard($('nc'), t, .25); $('ncf').style.scale = `${1 - .2 * SMOOTH(p(t, this.tsh, this.tsh + .7))} 1`;
    deck(t, this.cards);
    $('half').style.scale = `${SMOOTH(p(t, this.thalf - .1, this.thalf + .6))} 1`; this.utog.set(p(t, this.ttog, this.ttog + .4));
    $('v1').textContent = 'AED ' + fmt(counter(t, this.t30, .6, 0, 30000)); $('v2').textContent = 'AED ' + fmt(counter(t, this.t15, .6, 0, 15000));
    $('v1').style.opacity = t >= this.t30 - .05 ? 1 : 0; $('v2').style.opacity = t >= this.t15 - .05 ? 1 : 0;   // no "AED 0" sitting on screen before its count
    $('car').style.scale = `${SMOOTH(p(t, this.tcar, this.tcar + .5))} 1`; $('mort').style.opacity = EO(p(t, this.t12 - .1, this.t12 + .3));
    enter($('m20'), t, this.t5, { dy: 14, s0: .85 });
    typeIn($('dbt'), '3,000', t, ...this.tdb2, this.endAt);
  },
};

// ================================================================== R18  the 10% deposit
REELS.r18 = {
  bug: 'Law or custom', label: 'What’s law, and what’s custom',
  foot: 'Contract F is the Land Department’s unified sale contract (broker guide, 2021). No government document sets the deposit percentage. Illustrative cheque. Not legal advice.',
  setup() {
    std(this, 5);
    hookSetup(this, ['That 10% deposit?', 'It’s <g>not</g> <g>a</g> <g>law.</g>'], { max: 170, top: 320, extra: `
      <div class="glass ncard" id="nq" style="top:900px;padding-bottom:86px"><div class="tag" style="top:auto;bottom:28px">Illustrative</div><div class="eb">Cheque</div>
        <div class="row" style="margin-top:20px;font-size:32px"><span>Pay</span><span style="font-weight:600">The seller</span></div>
        <div class="big" style="margin-top:18px;font-size:84px;color:#fff">AED 200,000</div>
        <div style="margin-top:12px;font-size:28px;color:rgba(255,255,255,.7)">Memo: 10% deposit</div>
        <div class="stamp" id="cst" style="right:40px;top:-34px;color:var(--goldlight);background:rgba(2,22,20,.92)">CUSTOM</div></div>` });
    $('pscene').innerHTML = `
      <div class="card dcard" id="s1"><div class="eb">Law or custom?</div>
        <div class="cols"><div class="col"><div class="ch" style="color:var(--teal)">Set by an official document</div><div id="offnote" class="src">Nothing on the deposit.</div></div>
          <div class="col" style="border-color:var(--gold)"><div class="ch" style="color:var(--goldtxt)">Market custom</div><div class="tok" id="dep" style="background:var(--goldsoft);color:var(--goldtxt)">The 10% deposit cheque</div><div class="tok" id="agr" style="background:#fff;border:2px solid var(--goldsoft);color:var(--goldtxt);font-weight:500">Agreed between buyer and seller</div></div></div>
        <div class="note" id="pc" style="margin-top:22px;font-weight:600">No government document sets <span id="pcs">the percentage.</span></div></div>
      <div class="card dcard free" id="s2" style="height:880px"><div class="eb">What is official</div>
        <div class="ctr" id="ca" style="left:44px;top:110px">Contract A<div class="src">seller</div></div>
        <div class="ctr" id="cb" style="left:546px;top:110px">Contract B<div class="src">buyer</div></div>
        <div class="ctr" id="cf" style="left:220px;top:110px;width:400px;height:380px;border:3px solid var(--teal)"><div class="lbl">Unified sale contract</div><div class="big2">Contract F</div>
          <div class="src" style="margin-top:8px">made by a registered broker in Dubai REST</div></div>
        <div style="position:absolute;left:44px;right:44px;top:540px;display:flex;flex-direction:column;gap:16px">
          <div class="chip tint" id="f1" style="align-self:flex-start">The price</div><div class="chip tint" id="f2" style="align-self:flex-start">The payment plan</div><div class="chip gold" id="f3" style="align-self:flex-start">Who pays the transfer fee</div></div></div>`;
    this.cards = [{ id: 's1', at: this.paperAt + .1 }, { id: 's2', at: LN(4).on - .1 }]; deckSetup(this.cards);
    this.tlaw = wt(1, 'law'); ev(this.tlaw, 'stamp');
    this.tcu = wt(2, 'custom'); this.tag = wt(2, 'agreed'); ev(this.tcu, 'whip'); ev(this.tag, 'pop');
    this.tpc = LN(3).on; this.hpc = RN.highlight($('pcs'), { seed: 71 }); this.tpcs = wt(3, 'percentage'); ev(this.tpcs, 'scribble');
    this.tm = wt(4, 'Contract') + .1; ev(this.tm + .35, 'chime'); this.tf = [wt(4, 'price'), wt(4, 'payment'), wt(4, 'transfer')]; this.tf.forEach(x => ev(x, 'pop'));
    mbWindow(this.tcu, this.tcu + .4);
    this.posterAt = this.tlaw + .25;   // cover frame
  },
  scene(t) {
    hookIn(this.hw, t); nightCard($('nq'), t, .25); stamp($('cst'), t, this.tlaw, 8);
    deck(t, this.cards);
    const kd = EIO(p(t, this.tcu - .05, this.tcu + .4)); $('dep').style.opacity = t >= this.tcu - .05 ? 1 : 0; $('dep').style.translate = `${(1 - kd) * -420}px 0`;
    enter($('agr'), t, this.tag, { dy: 16, s0: .9 }); enter($('pc'), t, this.tpc, { dy: 12, s0: 1 }); enter($('offnote'), t, this.tpc, { dy: 8, s0: 1 });
    this.hpc.set(p(t, this.tpcs, this.tpcs + .45));
    const km = EIO(p(t, this.tm, this.tm + .45));
    enter($('ca'), t, LN(4).on + .1, { dy: 30 }); enter($('cb'), t, LN(4).on + .2, { dy: 30 });
    if (t >= this.tm) { $('ca').style.translate = `${km * 230}px 0`; $('cb').style.translate = `${-km * 270}px 0`; $('ca').style.opacity = 1 - km; $('cb').style.opacity = 1 - km; }
    $('cf').style.opacity = EO(p(t, this.tm + .25, this.tm + .5)); $('cf').style.scale = String(pscale(spr(t - this.tm - .25, { damping: 12, stiffness: 180 }), .7, 1));
    chips(t, [['f1', this.tf[0]], ['f2', this.tf[1]], ['f3', this.tf[2]]]);
  },
};

// ================================================================== R19  the permit red flag
function qrCells(seed) { const r = rng(seed); let s = ''; for (let y = 0; y < 11; y++) for (let x = 0; x < 11; x++) { const finder = (x < 3 && y < 3) || (x > 7 && y < 3) || (x < 3 && y > 7); const on = finder ? !(x % 10 === 1 && y % 10 === 1) && !((x === 9 && y === 1) || (x === 1 && y === 9)) : r() < .5; s += `<i style="background:${on ? '#1b2521' : 'transparent'}"></i>`; } return s; }
REELS.r19 = {
  bug: 'Verify a listing', label: 'Check an asking price',
  foot: 'The permit check runs in the Land Department’s Dubai REST app. Keyva compares an asking price with registered sales. Illustrative ad.',
  setup() {
    std(this, 5); this.endAt = wt(5, 'on', 0) - .05;
    hookSetup(this, ['No permit number?', 'That’s the', '<g>red</g> <g>flag.</g>'], { max: 170, top: 290, extra: `
      <div class="glass ncard" id="na" style="top:930px;padding-bottom:86px"><div class="tag" style="top:auto;bottom:28px">Illustrative ad</div><div class="eb">2 bed · sea view</div>
        <div class="big" style="margin-top:16px;font-size:80px;color:#fff">AED 1,850,000</div>
        <div class="row" style="margin-top:20px;font-size:32px"><span style="color:rgba(255,255,255,.75)">Permit no.</span><span id="np" class="mono">— — —</span></div>
        <div class="stamp" id="rf" style="right:40px;top:-34px;color:#f3b49a;background:rgba(2,22,20,.92)">RED FLAG</div></div>` });
    $('pscene').innerHTML = `
      <div class="card dcard" id="s1"><div class="tag">Illustrative ad</div><div class="eb">Every legitimate ad carries one</div>
        <div class="row" style="margin-top:30px;align-items:center;gap:30px"><div class="qr">${qrCells(91)}</div>
          <div style="flex:1"><div class="lbl">Trakheesi permit no.</div><div class="mono" id="pn" style="font-size:44px;font-weight:700;margin-top:10px">71<span class="blur">8204</span>6</div>
            <div class="src" style="margin-top:14px">Issued by the Land Department. Shown with its QR code.</div></div></div></div>
      <div class="card dcard free" id="s2" style="height:860px"><div class="eb">Scan it in the Dubai REST app</div>
        <div class="phone"><div class="scr"><div style="position:absolute;left:30px;top:120px">${`<div class="qr" style="width:190px;height:190px">${qrCells(91)}</div>`}</div><div class="scanline" id="sl"></div></div></div>
        <div style="position:absolute;left:44px;right:44px;top:700px;display:flex;gap:16px;justify-content:center">
          <div class="chip ok" id="k1">${OKI}Real</div><div class="chip ok" id="k2">${OKI}Active</div><div class="chip ok" id="k3">${OKI}For this property</div></div></div>
      <div class="card dcard" id="s3"><div class="eb">Two different checks</div>
        <div class="kv" style="margin-top:20px"><span>Permit</span><span class="chip ok">${OKI}Valid</span></div>
        <div class="kv"><span>Price</span><span class="chip gold" id="fp">Fair? Not the permit’s job</span></div>
        <div style="margin-top:30px;padding:24px 26px;border-radius:24px;background:var(--tint)" id="kv"><div class="lbl" style="color:var(--teal)">On Keyva</div>
          <div class="note" style="margin-top:10px">The asking price, against what similar homes <b>actually sold for</b>.</div></div></div>`;
    this.cards = [{ id: 's1', at: this.paperAt + .1 }, { id: 's2', at: LN(3).on - .1 }, { id: 's3', at: LN(4).on - .1 }]; deckSetup(this.cards);
    this.trf = wt(1, 'red'); this.cnp = RN.circle($('np'), { seed: 92, pad: 14, color: '#f3b49a' }); ev(this.trf - .3, 'scribble'); ev(this.trf, 'stamp');
    this.tpn = wt(2, 'Trakheesi'); this.upn = RN.underline($('pn'), { seed: 93 });
    this.tscan = wt(3, 'scan'); ev(this.tscan, 'click'); this.tk = [wt(3, 'real'), wt(3, 'active'), wt(3, 'property')]; this.tk.forEach(x => ev(x, 'pop'));
    this.tfp = wt(4, 'fair'); ev(this.tfp, 'hit'); this.tkv = LN(5).on; ev(this.tkv, 'chime');
    this.posterAt = this.trf + .45;   // cover frame
  },
  scene(t) {
    hookIn(this.hw, t); nightCard($('na'), t, .25); this.cnp.set(p(t, this.trf - .3, this.trf + .2)); stamp($('rf'), t, this.trf, 7);
    deck(t, this.cards); this.upn.set(p(t, this.tpn, this.tpn + .45));
    $('sl').style.top = (40 + 380 * (.5 - .5 * Math.cos((t - this.tscan) * 3))) + 'px'; $('sl').style.opacity = t >= this.tscan ? 1 : 0;
    chips(t, [['k1', this.tk[0]], ['k2', this.tk[1]], ['k3', this.tk[2]]]);
    enter($('fp'), t, this.tfp, { dy: 10, s0: .85 }); enter($('kv'), t, this.tkv, { dy: 20, s0: .97 });
  },
};

// ================================================================== R20  Dubai publishes it
REELS.r20 = {
  bug: 'Every area', label: 'Real prices, area by area',
  foot: 'Dubai Land Department open data, via Data Dubai. Example: Dubai Marina, ready homes, registered sales in the 12 months to 2 Oct 2026.',
  setup() {
    std(this, 5);
    hookSetup(this, ['Dubai publishes', 'what homes <g>actually</g>', 'sell for.'], { max: 170, top: 290, extra: `
      <div class="glass ncard" id="nd" style="top:930px"><div class="eb">Registered sales · open data</div>
        ${[.86, .64, .78, .55, .9].map((w, i) => `<div class="sk" id="sk${i}" style="width:${w * 100}%"></div>`).join('')}
        <div class="stamp" id="pr" style="right:40px;top:120px;color:var(--goldlight);background:rgba(2,22,20,.85)">PUBLIC RECORD</div></div>` });
    $('pscene').innerHTML = `
      <div class="card dcard" id="s1"><div class="eb">Two different prices</div>
        <div class="two"><div class="pane" id="pa" style="background:#f4f3ef"><div class="lbl">On a listing</div><div class="h" style="font-size:52px;margin-top:14px;color:#8d938f" id="ask">Asking price</div><div class="src" style="margin-top:12px">what’s asked</div></div>
          <div class="pane" id="pb" style="background:var(--tint)"><div class="lbl" style="color:var(--teal)">On record</div><div class="h" style="font-size:52px;margin-top:14px;color:var(--teal)">Registered sale</div><div class="src" style="margin-top:12px" id="od">Land Department open data</div></div></div></div>
      <div class="card dcard" id="s2"><div class="eb">Dubai Marina · ready homes</div>
        <div class="lbl" style="margin-top:22px">Typical price, registered sales</div>
        <div class="big" style="font-size:110px;color:var(--teal);margin-top:12px">AED 2,005<span style="font:500 34px InterK;color:var(--muted)"> /sq ft</span></div>
        <div class="kv" style="margin-top:22px"><span>Number of sales</span><span class="v" id="ns2">2,690</span></div>
        <div class="kv"><span>Dates</span><span class="v" id="dt2" style="font-size:30px">12 months to 2 Oct 2026</span></div>
        <div class="chip tint" id="aba" style="margin-top:24px">Area by area</div></div>`;
    this.cards = [{ id: 's1', at: this.paperAt + .1 }, { id: 's2', at: LN(4).on - .1 }]; deckSetup(this.cards);
    this.tpr = wt(1, 'sell'); ev(this.tpr, 'stamp');
    // "Not asking prices": the listing pane steps back, it is not crossed out. Asking prices are a feature of
    // Keyva (shown beside the registered price, labelled); what Dubai publishes is the other one.
    this.task = wt(2, 'asking');
    this.treg = wt(2, 'registered'); ev(this.treg, 'chime'); this.tod = wt(2, 'open'); this.uod = RN.underline($('od'), { seed: 102 });
    // gold, a pointer not a warning: the asking price is a Keyva feature
    this.tasked = wt(3, 'asked'); this.cask = RN.circle($('ask'), { seed: 103, pad: 16 }); ev(this.tasked, 'scribble');
    this.tn = wt(4, 'number'); this.td = wt(4, 'date'); this.ta = wt(4, 'area');
    this.un = RN.underline($('ns2'), { seed: 104 }); this.ud = RN.underline($('dt2'), { seed: 105 }); ev(this.tn, 'scribble'); ev(this.td, 'scribble'); ev(this.ta, 'pop');
    this.posterAt = this.tpr + .45;   // cover frame
  },
  scene(t) {
    hookIn(this.hw, t); nightCard($('nd'), t, .25);
    for (let i = 0; i < 5; i++) { const el = $('sk' + i); el.style.scale = `${SMOOTH(p(t, .4 + i * .12, 1 + i * .12))} 1`; el.style.transformOrigin = 'left'; }
    stamp($('pr'), t, this.tpr, -6);
    deck(t, this.cards);
    { const k = EIO(p(t, this.task, this.task + .35)) * (1 - EIO(p(t, this.tasked - .35, this.tasked))); $('pa').style.opacity = String(1 - .5 * k); $('pa').style.scale = String(1 - .04 * k); }
    $('pb').style.boxShadow = t >= this.treg ? `0 0 0 ${4 * EO(p(t, this.treg, this.treg + .3))}px var(--teal)` : 'none';
    this.uod.set(p(t, this.tod, this.tod + .45)); this.cask.set(p(t, this.tasked, this.tasked + .5));
    this.un.set(p(t, this.tn, this.tn + .4)); this.ud.set(p(t, this.td, this.td + .45)); enter($('aba'), t, this.ta, { dy: 12, s0: .9 });
  },
};
