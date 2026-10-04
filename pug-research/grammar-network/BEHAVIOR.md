# Behavioral experiments: findings

## 1. Markov transitions
- Markov: host-chain order-1: wiki-src 8066 transitions, traces-src 0 —
  the traces sample has NO nested relay URLs (all direct fetches), so the
  cross-source comparison is degenerate by construction; the relay-chain
  Markov exists only in wiki-sourced URLs. Within wiki: order-2 confirms
  the 3-layer rule (jqp > md.succ.ai > sec.gov 646x). NOTE: one order-2
  state is `allorigins%2ehexlet%2eapp` — percent-encoded host variant
  leaking through as a distinct state (normalization gap, logged).
- wiki order-2 top: jqp.vercel.app > md.succ.ai -> www.sec.gov (646); jqp.vercel.app > allorigins.hexlet.app -> www.sec.gov (142); jqp.vercel.app > vanderbi.lt -> www.sec.gov (111); jqp.vercel.app > r.jina.ai -> www.sec.gov (66); jqp.vercel.app > allorigins%2ehexlet%2eapp -> www.sec.gov (48)
- chat speaker order-1: agent->agent 167136; user->agent 6351; agent->user 6351; user->user 3631
- claude msgtype order-1 top: assistant->assistant 99702; assistant->user 68320; user->assistant 68311; user->user 3893; system->system 1890; user->system 948
- claude msgtype order-2 top: assistant > assistant -> user (65394); user > assistant -> assistant (65361); assistant > user -> assistant (64028); assistant > assistant -> assistant (34106); assistant > user -> user (3392)

## 2. Retry loops
- traces: 1099 of 13043 URL templates requested more than once (top: [('https://civilrightsdata.ed.gov/api/v1.0/getstateestimation?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}', 4685), ('https://civilrightsdata.ed.gov/api/v1.0/getstateestimation?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}&zz={text}', 2203), ('https://civilrightsdata.ed.gov/api/v1.0/getstateestimation?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}&zzbulk={text}', 1742)])
- turns: 324021 A->X->A action cycles in 62616/78016 sessions

## 3. Session/turn lengths
- chat/room: {'n': 16, 'min': 1, 'p50': 22, 'p90': 20078, 'max': 149307, 'mean': 11467.8125}
- claude/session: {'n': 53, 'min': 1, 'p50': 2, 'p90': 2, 'max': 244709, 'mean': 4619.245283018868}
- turns/session: {'n': 78016, 'min': 1, 'p50': 33, 'p90': 37, 'max': 286, 'mean': 27.360515791632487}
- wiki revs/page: {'n': 4579, 'min': 1, 'p50': 1, 'p90': 4, 'max': 2327, 'mean': 3.1865036034068575}

## 4. First/last actions
- chat first speaker: {'user': 10, 'agent': 6}; last: {'agent': 6, 'user': 10}
- claude first msgtype: {'system': 53}; last: {'result': 49, 'system': 4}
- turns first action: [('mouse_move', 56492), ('sh:Check', 3936), ('screenshot', 2799), ('sh:cd', 2534), ('left_click', 1382)]
- turns last action: [('send_message_back_to_chat', 9913), ('left_click', 8445), ('None', 8271), ('key', 6065), ('sh:cd', 4508)]

## 5. Burstiness (inter-arrival)
- traces/global: n=29499 CV=57.32 sub60s=0.99 med_gap=1.0s
- traces/reportcard.msde.maryland.gov: n=14353 CV=27.31 sub60s=1.00 med_gap=0.0s
- traces/civilrightsdata.ed.gov: n=12542 CV=36.41 sub60s=0.99 med_gap=1.0s
- traces/www.kansasmemory.gov: n=1790 CV=17.51 sub60s=1.00 med_gap=1.0s
- traces/msp2018.msde.maryland.gov: n=335 CV=1.10 sub60s=0.99 med_gap=10.0s
- traces/www.history.navy.mil: n=189 CV=9.18 sub60s=0.43 med_gap=78.0s
- chat/global: n=183485 CV=22.61 sub60s=0.86 med_gap=16.9s
- wiki/global: n=14591 CV=26.98 sub60s=0.84 med_gap=4.0s

## 6. Failure vocabulary
- 5277 error-marked docs; top enriched tokens: failures(1.80), failure(1.80), fails(1.80), failed(1.80), fail(1.80), errors(1.80), error(1.80), blocked(1.80), syntax(1.45), country(1.12), attempt(1.10), completely(1.09), poland(1.05), workaround(1.00), escalation(0.97)

## One-line findings
- Markov: the relay-chain Markov exists only in wiki-sourced URLs
  (traces sample: zero nested chains — direct fetches only). Order-2
  transitions confirm the 3-layer nesting rule; see BEHAVIOR.md.
- Retry loops: 1099 repeated URL templates in traces and 324021 A→X→A action cycles across 62616 turn sessions — retry is a first-class behavior, not an edge case.
- Turn lengths: chat rooms median 22 msgs, claude sessions median 2, turn sessions median 33 — compare shapes in BEHAVIOR.md.
- First/last: rooms start [('user', 10)] / end [('user', 10)]; turn sessions start [('mouse_move', 56492)] / end [('send_message_back_to_chat', 9913)].
- Burstiness: traces/global: n=29499 CV=57.32 sub60s=0.99 med_gap=1.0s — machine cadence is measurable per host; see BEHAVIOR.md.
- Failure vocab: top error-enriched tokens: failures, failure, fails, failed, fail, errors, error, blocked.
