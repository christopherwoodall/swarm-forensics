# Physical swarm cases: documented hardware, bounded capabilities

Research date: 2026-10-01. These are real executed demonstrations, not discovered online communities. “AI” here includes engineered autonomous control and programmed swarm intelligence, not necessarily neural learning or LLMs.

## Case P1 — Kilobots assembling shapes, 2014

### Setting and actual scale

Rubenstein, Cornejo, and Nagpal published **Programmable self-assembly in a thousand-robot swarm** in Science in August 2014. The accessible journal abstract confirms the thousand-robot result; detailed methods and timings come from the full journal supplement, not an obtained copy of the gated main article.[58][59]

The supplement describes **13 hardware assembly demonstrations** on a prepared **2.4 × 2.4 m table**. Two largest trials began with **1,024 robots**: a K shape finished with **1,018 shape members after 11.71 hours**, and a starfish with **946 after 11.66 hours**.[59]

Initial population and final shape membership differ. Conservative shape scaling left surplus robots that were removed after completion; the difference is not a measured casualty or malfunction count. Ten smaller repeatability trials began with 116 robots.[59]

### Individual agents and layered control

Each Kilobot moves with vibrating motors and has infrared communication and proximity sensing. The robots lack a bird's-eye view of the group.[56]

All robots receive a common shape specification and assembly program. **Four stationary seed robots** start in distinct states and establish a coordinate system; local gradient formation, localization, and edge-following then allow additional robots to assemble the shape.[59]

An overhead controller uploads the program and can start/stop the robots. The methods do not describe it issuing individual motion commands during assembly. Thus centralized initialization coexists with decentralized execution.[59]

### Coupling and collective behavior

Nearby robots broadcast state, gradients, and localized positions. This is explicit short-range communication plus physical neighborhood sensing; describing the system as robots laying chemical pheromones would be inaccurate.[59]

The global shape emerges through local execution of a supplied specification. The seeds are reference anchors, so the system is not completely symmetric. **Classification: observed programmed robotic swarm intelligence with initialization and reference roles.**[59]

### Observation and results

A calibrated overhead camera recorded images every five seconds to measure true positions. A listening robot queried final internal states. Comparing true and internally estimated positions through alignment and error measurement made the coordination inspectable rather than relying only on a final photograph.[59]

The authors report completion without human intervention in all 13 trials despite communication loss, inaccurate movement/sensing, stalls, and physical disturbance. However, only two trials had 1,024 starting robots; the other experiments do not establish repeated thousand-robot reliability.[59]

### Limits and relevance to detection

Assembly required hours on a controlled surface; resulting shapes could be warped. The mathematical correctness argument assumes idealized robots and restricted shape conditions, not arbitrary terrain or unrestricted hardware failure.[59]

This case offers unusually clear measurement of group outcome, local agent state, and control architecture. It demonstrates why “a controller was present” is not enough to dismiss decentralized execution: one must identify what that controller actually chose.

## Case P2 — Micro flying robots navigating in the wild, 2022

### Setting and separate experimental scales

Zhou and colleagues' Science Robotics study reports **ten palm-sized drones flying through a bamboo forest**, with a goal 65 m forward outside it. Another ten-drone trial tested repeated reciprocal avoidance over three minutes while people introduced obstacles, moved through the area, and disturbed a drone.[51]

The human-tracking trial used **four drones**. The illustrated **40-drone swarm playground was software**, not a measured 40-drone hardware forest flight. Hardware and simulation benchmarks should not be combined into a larger deployment claim.[51]

### Agents, control, and communications

Each drone carries perception, localization, planning, and control. Visual-inertial odometry, onboard depth mapping, and UWB relative-distance measurements support motion estimation and drift correction.[51]

Each onboard planner repeatedly optimizes trajectory geometry and timing using objectives such as obstacle avoidance, collision avoidance, smoothness, flight time, and optional formation/tracking terms. A user or software supplies goals; local trajectory decisions and flight control execute onboard.[51]

Compact planned trajectories are broadcast so neighboring drones can predict one another and avoid conflicts. The study discusses both single-access-point star networking and peer-to-peer ad hoc networking; decentralized motion planning therefore does not mean absence of network infrastructure.[51]

**Classification: observed decentralized robotic coordination with onboard optimization and explicit communication.** Adaptation means replanning in response to current observations; the paper does not demonstrate LLMs or online model-weight learning.[51]

### Demonstrated collective capabilities

The field trials show narrow-gap negotiation, implicit queueing through trajectory timing, formation deformation/reformation around obstacles, and multiview tracking under occlusion.[51]

The systems operate with a safety hierarchy that can replan or emergency-stop when a trajectory is infeasible. Flight time is approximately eleven minutes, and the authors prioritize field performance over rigorous completeness/optimality proofs.[51]

### How coordination was measured

The evidence includes recorded maps and trajectories, formation deviation, velocity profiles, minimum inter-drone distances, reached-goal counts, and linked experimental movies. Simulation comparisons with other planners are a different evidence class from hardware flight measurements.[51]

The paper's Figure 5 presents two separate flights; those panels should not be reconstructed as one continuous trial. Unlabeled numbers from automatically extracted plot tables were not used as precise quantitative evidence in this collection.[51]

### Limits and relevance

Disaster relief, extraterrestrial transport, and ecological inspection are motivations or possible applications, not verified mission deployments. Ten-drone trials do not establish unlimited-scale or all-weather reliability.[51]

The case shows a useful observability standard: collective motion, individual planned motion, communication, and perturbation response are described together. A video of many drones moving similarly would establish much less about the coordination mechanism.

## Case P3 — Perdix: a 103-drone military demonstration

### Dates, place, and actual count

A Department of Defense release dated **2017-01-09**, preserved by PACOM, reports an **October 2016** test at China Lake, California. **103 Perdix microdrones** were launched from **three F/A-18 Super Hornets**.[52]

The announcement year is not the test year. This is a documented military hardware demonstration, **not proof of battlefield deployment**.[52]

### Reported architecture and behavior

The release attributes collective decision-making, adaptive formation flight, and self-healing to the drones. Program director William Roper describes collaboration without a leader and adaptation to members entering or exiting.[52]

His “one distributed brain” language is an analogy, not evidence of a neural architecture or a conscious collective. The announcement also frames future battle networks as involving humans in the loop.[52]

**Classification: officially reported leaderless swarm demonstration, with less publicly inspectable mechanism evidence than the scientific cases above.**[52]

### Observation and evidence quality

The announcement names the test organizations and describes demonstration footage documented on 60 Minutes. This research did not independently analyze that footage.[52]

No open telemetry, radio protocol, local rules, controller code, or detailed quantitative member-loss test is provided in the release. Consequently, stronger claims about every drone communicating with every other drone, or about quantified self-healing performance, cannot be established from it.[52]

### Conditions and limits

The source reports launch-related stresses including **Mach 0.6**, **−10°C**, and ejection shocks. Those conditions do not mean the microdrones sustain Mach 0.6 throughout autonomous flight.[52]

Manufacturing batches of **up to 1,000** were a production ambition, not the measured demonstration population. The release discusses transition toward programs of record, rather than establishing an already fielded thousand-agent force.[52]

### Detection relevance

The useful evidence is a dated, named official test and a reported architecture. A more rigorous assessment of decentralization or resilience would require messages, trajectories, controller boundaries, and controlled perturbations. Those are proposed evidence requirements, not measurements recovered here.

## Comparative assessment

| Case | Real hardware scale in this account | Mechanism visibility | Main overclaim to avoid |
|---|---|---|---|
| Kilobots | Two trials starting with 1,024.[59] | Detailed algorithm, local states, camera measurements. | Treating final members as casualties, or the idealized proof as universal hardware safety. |
| Forest drones | Ten-drone navigation/avoidance; four-drone tracking.[51] | Onboard planning and trajectory exchange described. | Calling the 40-drone software example a field deployment. |
| Perdix | 103 in the October 2016 test.[52] | Official description; no public implementation/telemetry here. | Calling proposed 1,000-unit production a tested or battlefield-deployed swarm. |

The examples demonstrate that classical artificial swarms can exist without LLMs and that decentralization must be assessed by control layer. Their detection is principally **instrumented observation of collective behavior**, unlike the output-only inference often possible in social-media investigations.

Continue with [controlled LLM-agent experiments](05-digital-agent-experiments.md) and the [source guide](09-source-guide.md).

## Sources

[51] https://zhepeiwang.github.io/pubs/sr_2022_swarm.pdf — Swarm of micro flying robots in the wild — Zhou et al., Science Robotics 7, eabm5954
[52] https://www.pacom.mil/Media/NEWS/Article/1046043/department-of-defense-announces-successful-micro-drone-demonstration — Department of Defense Announces Successful Micro-Drone Demonstration — Press Operations NR-008-17, official PACOM mirror
[56] https://seas.harvard.edu/news/self-organizing-thousand-robot-swarm — A self-organizing thousand-robot swarm — Harvard SEAS
[58] https://www.science.org/doi/10.1126/science.1254295 — Programmable self-assembly in a thousand-robot swarm — Rubenstein, Cornejo and Nagpal, Science 345(6198), 795–799
[59] https://www.science.org/doi/suppl/10.1126/science.1254295/suppl_file/rubenstein.sm.pdf — Supplementary Materials for Programmable self-assembly in a thousand-robot swarm — Rubenstein, Cornejo and Nagpal
