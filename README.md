# Entropy-based RPS bot

Inspired by [Solving Wordle using information theory by 3Blue1Brown](https://www.youtube.com/watch?v=v68zYyaEmEA). This rock, paper, scissors bot is my attempt at implementing information theory and possibly game theory into a project. I plan on adding an interface just like in 3Blue1Brown's video. Aswell, as adding a Markov-Chain EU variable and to test my bot against other bot strategies to see where can it be improved and what data i can collect.

In my experience, if you try to play vs this bot consciously, chances are you will think the bot is making a move after you type in your own; Feels like the bot is cheating. I dont think i have every win a 15+ round game. Feel free to try.

## Bot Math & Logic

Below is a short breakdown of what `decide_move` does and the math behind each step.

---

### 1. Inputs & Notation

* **Counts:** $(c_R, c_P, c_S)$ stored in `moves_count_decay` / `moves_count_real`.
* **Total observed moves:** $\left(N=\sum c_m\right)$.
* **Smoothing constant:** $(a)$ (`self.a`).
* **Recent-weight:** $(b)$ (`self.b`) and recent empirical probs `self.empirical_prob_recent`.
* **Rounds / tracking:** `valid_rounds`, total `self.rounds`, `self.k`.
* **Hyperparameters:** $\beta_{\max}$, $\epsilon$ (exploration).

---

### 2. Estimate Opponent Distribution 

Based on the moves played compute a smoothed empirical distribution:

$$\hat p(m)=\frac{c_m + a}{N + 3a},\qquad m\in{R,P,S}.$$

This is **Laplace (add-a) smoothing**: it avoids zero probabilities at the start and stabilizes estimates.

---

### 3. Entropy 

**Shannon entropy (bits):**

$$H = -\sum_{m} \hat p(m)\log_2 \hat p(m).$$

Maximum for a uniform 3-way distribution is $\left(H_{\max}=\log_2 3\approx 1.585\right)$.

 When **Large $(H)$** $\approx$ opponent is random; **small $(H)$** $\approx$ opponent is predictable, so bot becomes more exploitative.

---

### 4. Expected-Utility (Alltime + Recent Blend)

iT computeS two EU variants and combine them:

**All-time EU** :

Because scoring is +1 for wins, 0 otherwise, the expected reward of playing move $(j)$ equals the probability the opponent plays the move $(j)$ beats. Practically:

$$EU_{\text{all}} = \big[\hat p(S)-\hat p(P),\; \hat p(R)-\hat p(S),\; \hat p(P)-\hat p(R)\big]$$

corresponding to [Rock, Paper, Scissors].

**Recent EU** from `self.empirical_prob_recent` is computed the same way (but from a recent window $(k)$, calculated based on total rounds).

The formula for calculating the recent window size **$k$** is:

$$k = \text{round}\left(\text{rounds} \cdot \frac{C}{\ln(\text{rounds} + e)}\right)$$

**Combined EU** used earlier in the function:

$$EU_{\text{combined}} = EU_{\text{all}} + b\cdot EU_{\text{recent}}.$$

---

### 5. Adaptive Stochastic Policy (Entropy $\rightarrow$ Softmax)

When not in early random warmup and not doing an $\varepsilon$-random exploration, the bot:

1.  **Maps entropy to an inverse temperature $(\beta)$** (linear map):

$$\beta = \beta_{\max}\cdot\frac{H_{\max}-H}{H_{\max}}.$$

* If $H\approx H_{\max}$ $\rightarrow$ $\beta\approx 0$ (near uniform).
* If $H\approx 0$ $\rightarrow$ $\beta\approx\beta_{\max}$ (sharp / exploit).

2.  **Converts utilities to a probability distribution** with a numerically stable softmax:

$$P(a_j)=\frac{\exp\big(\beta(EU_j-\max_k EU_k)\big)}{\sum_k \exp\big(\beta(EU_k-\max_k EU_k)\big)}.$$

(Subtracting $(\max EU)$ prevents overflow and is equivalent mathematically.)

3.  **Samples an action** from $P(a_j)$. This yields a smooth bias: as entropy falls, the softmax concentrates on the best counter; as entropy rises, the bot randomizes.

---

### 6. Exploration & Warmup

* **Warmup:** If `valid_rounds < round(k/2)` the bot plays **uniformly random** (gather data).
* **Ongoing exploration:** With probability $(\varepsilon)$ the bot makes a **random move** regardless of softmax. Computed as $\left(\varepsilon=\max(0.1,0.25(1-\text{progress}))\right)$ — more exploration early, lower bound 0.1.

---


## TLDR

The bot estimate the opponent distribution (smoothed), measure unpredictability via **Shannon entropy**, map entropy to an **inverse temperature $(\beta)$**, convert expected win-probabilities to a **softmax distribution** controlled by $(\beta)$, then sample a move — with additional warmup and $\varepsilon$-random exploration to keep behavior robust.
