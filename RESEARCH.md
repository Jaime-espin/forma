# Research — The Science Behind FORMA

As a self-trained athlete who tries to perform and compete, I try to learn as much as I can about the science behind training. As a software engineering student, I am also interested in how to apply these algorithms to measure performance. That is the aim of this project: to understand the science of training well enough to build software that interprets the data meaningfully.

Training cannot be fully captured in numbers, perception of effort matters, context matters, and the same workout affects two athletes very differently. But there are models that get surprisingly close, and understanding them is the foundation of this project.

---

## The Core Problem

How do you know if you are ready to perform tomorrow?

Your body is always balancing two opposing forces:

- **Training makes you fitter** — through adaptation: muscle repair, cardiovascular improvement, efficiency gains.
- **Training makes you tired** — through accumulated stress: cellular damage, glycogen depletion, central nervous system fatigue.

The key insight is that **fatigue accumulates faster than fitness, but also dissipates faster**. This is why tapering before a race works: you reduce load, fatigue drops quickly, and fitness — which decays more slowly — stays near its peak. The brief window where fitness is high and fatigue is low is when you perform best.

The question is: can we model this mathematically?

---

## The Banister Fitness-Fatigue Model (1975)

Eric Banister, a Canadian exercise physiologist, was the first to formalise this into a mathematical model. His paper *"Modeling Elite Athletic Performance"* (1991) proposed what is now called the **Two-Component Model** or **Fitness-Fatigue Model**:

$$P(t) = p_0 + k_1 \cdot g(t) - k_2 \cdot h(t)$$

Where:

| Symbol | Meaning |
|---|---|
| $P(t)$ | Predicted performance at time $t$ |
| $p_0$ | Baseline performance |
| $g(t)$ | Fitness component (positive response to training) |
| $h(t)$ | Fatigue component (negative response to training) |
| $k_1, k_2$ | Individual gain constants (calibrated from real performance data) |

Both $g(t)$ and $h(t)$ are computed as **exponentially weighted sums** of past training loads. The model says: performance equals your fitness minus your fatigue, weighted by how strongly each affects you personally.

This is the theoretical foundation. In practice, calibrating $k_1$ and $k_2$ requires repeated performance tests over months, which makes it more of a research tool than an everyday training aid.

---

## CTL / ATL / TSB — The Practical Implementation

Andrew Coggan  (the same physiologist who defined FTP) popularised a simplified version of Banister's model that became the standard in endurance sports. It is used by TrainingPeaks, Garmin, Wahoo, and many others.

The simplification: instead of calibrating individual constants, it uses fixed time windows derived from physiological research.

| Variable | Full Name | What it represents | Time window |
|---|---|---|---|
| **CTL** | Chronic Training Load | Long-term fitness | ~42 days |
| **ATL** | Acute Training Load | Short-term fatigue | ~7 days |
| **TSB** | Training Stress Balance | Form = CTL − ATL | — |

The 42-day and 7-day windows are not arbitrary, they approximate the timescales at which aerobic adaptations build and acute fatigue resolves, respectively, based on empirical observation across many athletes.

### The Mathematics — Exponential Moving Average

Both CTL and ATL are calculated as **exponentially weighted moving averages (EMA)** of daily training load. The update rule for each day is:

$$CTL_t = CTL_{t-1} \cdot e^{-1/42} + TSS_t \cdot \left(1 - e^{-1/42}\right)$$

$$ATL_t = ATL_{t-1} \cdot e^{-1/7} + TSS_t \cdot \left(1 - e^{-1/7}\right)$$

On rest days, $TSS_t = 0$, so both values decay naturally. CTL decays slowly (fitness is hard to lose), ATL decays quickly (fatigue resolves within days).

**TSB (Form):**

$$TSB = CTL - ATL$$

| TSB range | Interpretation |
|---|---|
| Very negative (< −20) | High fatigue — risk of overtraining or injury |
| Slightly negative | Building phase — normal during hard training blocks |
| Zero | Equilibrium |
| Slightly positive (+5 to +25) | Peak form window — ideal for racing |
| Very positive (> +25) | Detraining — too much rest, fitness declining |

The "sweet spot" before a target race is a TSB between roughly +5 and +20. Too much taper and fitness starts to drop; too little and fatigue masks it.

---

## Training Stress Score (TSS) — The Input

CTL and ATL are only as good as the daily training load input that feeds them. This input is called **TSS (Training Stress Score)**, originally defined by Coggan for cycling with a power meter:

$$TSS = \frac{t \times NP \times IF}{FTP \times 3600} \times 100$$

Where $NP$ is Normalised Power, $IF$ is Intensity Factor ($NP / FTP$), and $t$ is duration in seconds. A one-hour ride exactly at FTP scores 100 TSS.

The challenge: **TSS requires a power meter**. For running and multi-sport athletes, several proxies exist:

| Method | Based on | Requires |
|---|---|---|
| **rTSS** (running TSS) | Pace and lactate threshold pace | GPS + known threshold pace |
| **hrTSS** (heart rate TSS) | Time in heart rate zones | Heart rate monitor + threshold HR |
| **Relative Effort** | Strava's proprietary formula | Heart rate data (Strava-specific) |

For FORMA, **hrTSS** is the most practical approach because heart rate data is available for almost all activities regardless of sport type, and it does not require sport-specific calibration.

The hrTSS formula approximates TSS using the ratio of average heart rate to threshold heart rate and time spent at effort:

$$hrTSS \approx \frac{t \times \left(\frac{HR_{avg}}{HR_{threshold}}\right)^2 \times 100}{3600}$$

This is a simplification, but it is consistent and sport-agnostic — which matters when your dataset includes running, cycling, trail running, hiking, kayaking, and ski touring.

---

## Supercompensation — The Biological Basis

The CTL/ATL model is a mathematical abstraction of a well-established physiological phenomenon: **supercompensation**.

The cycle works as follows:

1. **Training stimulus** — workout applies stress, temporarily reducing performance capacity
2. **Fatigue phase** — body is in recovery; performance is below baseline
3. **Supercompensation** — if recovery is adequate, the body adapts *beyond* its previous baseline
4. **Detraining** — if no new stimulus is applied, fitness returns to baseline

The timing of the next training session within this cycle determines whether training leads to adaptation or accumulating fatigue. Too early = overtraining. Too late = no adaptation. This is the biological reality that CTL/ATL/TSB tries to track.

---

## Limitations of the Model

It is important to be honest about what these models cannot capture:

- **Individual variation** is large. The 42/7 day windows are averages; some athletes recover faster, some slower.
- **Sleep, nutrition, life stress** are invisible to the model. An athlete with a perfect TSB can still perform poorly if they slept four hours.
- **Sport specificity** is ignored. Running fatigue and cycling fatigue use different muscle groups; a model that sums TSS across sports will overestimate accumulated fatigue.
- **Non-linear responses** are not captured. The model assumes linearity, but training adaptations are not linear — especially at extreme loads.
- **Injury risk** is not modelled. ACWR (Acute:Chronic Workload Ratio) is a separate model better suited for predicting injury risk, particularly for running-related load spikes.

These limitations are why more sophisticated tools exist (HRV monitoring, lactate testing, performance testing) and why platforms like Intervals.icu allow users to customise the time constants.

---

## Alternatives and Extensions

| Model | Description | Use case |
|---|---|---|
| **Banister (full)** | Calibrated $k_1$, $k_2$ constants; predicts actual performance | Research, elite coaching |
| **CTL/ATL/TSB (Coggan)** | Fixed time constants; tracks fitness/fatigue balance | General endurance training |
| **ACWR** (Acute:Chronic Workload Ratio) | ATL/CTL ratio; focus on injury risk | Running load management |
| **HRV-based load** | Uses heart rate variability as fatigue proxy | Daily readiness monitoring |
| **PMC with custom τ** | Same model, user-tuned time constants | Advanced self-coaching |

---

## Why This Matters for FORMA

FORMA uses hrTSS as the input signal and implements the CTL/ATL/TSB model to generate a **Performance Management Chart** — the same visualisation used by TrainingPeaks and Garmin Connect — but driven entirely by personal data, with full transparency into how every number is calculated.

The goal is not just to replicate what commercial platforms do. It is to understand *why* the model works, where it breaks down, and eventually extend it — starting with an AI layer that interprets the numbers in context rather than just displaying them.

---

## Key References

- Banister, E.W. (1991). *Modeling elite athletic performance*. In H. Green, J. McDougal, & H. Wenger (Eds.), *Physiological Testing of Elite Athletes*. Human Kinetics.
- Coggan, A. (2003). *The Science of the Performance Manager*. TrainingPeaks. → [Article](https://www.trainingpeaks.com/learn/articles/the-science-of-the-performance-manager/)
- Bourdon, P.C. et al. (2017). *Monitoring Athlete Training Loads: Consensus Statement*. International Journal of Sports Physiology and Performance.
- Busso, T. (2003). *Variable dose-response relationship between exercise training and performance*. Medicine & Science in Sports & Exercise.
- [Intervals.icu — Fitness/Fatigue documentation](https://forum.intervals.icu/t/fitness-fatigue-and-form/63)