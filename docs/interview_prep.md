# Interview Prep: Bank Fraud Detection Project

## "Walk me through this project."

I built an end-to-end fraud detection analytics project on a real bank transaction dataset. The dataset had no pre-existing fraud labels, so instead of training a model on known fraud, I designed my own statistical risk-scoring system using outlier detection — flagging transactions that were unusual on amount, login attempts, or duration. I then analyzed the results across four different tools — Python, SQL, Excel, and Power BI — and cross-validated that every tool produced the exact same numbers, which gave me confidence the analysis was correct and not a tool-specific bug.

## "Why didn't you just use a labeled fraud dataset?"

I actually found this dataset didn't include a fraud label, and I made a deliberate choice to keep it rather than switch datasets. This is closer to a real-world situation — a junior analyst is often handed messy, unlabeled data and has to define "suspicious" themselves using domain reasoning and statistics, rather than always having a clean answer key.

## "What's the difference between IQR and Z-score outlier detection, and why did you choose IQR?"

Z-score measures how many standard deviations a value is from the mean, and works best on roughly normally-distributed data. IQR is based on the middle 50% of the data (Q1 to Q3) and is more robust to skewed distributions. Since transaction amounts in banking are almost always skewed — many small transactions, a few very large ones — IQR was the more appropriate choice.

## "Tell me about a mistake you made and how you caught it."

Early in the EDA phase, I found that hour 16 had the most raw suspicious transactions, and initially it looked like a time-based fraud pattern. But when I checked the total transaction volume per hour, I found hour 16 also had the most transactions overall — so the raw count was misleading. I recalculated using suspicious *rate* instead of raw count, and the ranking changed meaningfully. It taught me to always check for volume bias before drawing a conclusion from a count-based comparison.

## "What are the limitations of your fraud-scoring approach?"

A few, and I documented them directly rather than hiding them:
- The LoginAttempts signal had a technical limitation — the IQR bounds collapsed because the middle 50% of the data had almost no variance, causing it to over-flag mild, normal behavior (2 login attempts).
- My scoring system is a reasonable statistical approximation, not verified ground truth, since there were no real fraud labels to validate against.
- The dataset only contained transactions from a narrow 3-hour window, which limited how confidently I could draw time-of-day conclusions.

## "Why cross-validate across four tools instead of just picking one?"

Different tools can introduce different bugs — I actually ran into this directly: my first Excel pivot table gave a wrong answer because Excel treated a text "True"/"False" column differently from a real boolean. If I'd trusted a single tool, I might not have caught that. Getting matching numbers across Python, SQL, Excel, and Power BI gave me real confidence the underlying analysis was correct, not just that one tool happened to compute something consistently.

## "What would you do differently with more time?"

I'd want to test my rule-based scoring system against a proper labeled fraud dataset to see how well it actually performs (precision/recall), rather than relying on statistical plausibility alone. I'd also want to explore a basic machine learning model (like isolation forests, which are designed for unlabeled anomaly detection) as a comparison against my manual rule-based approach.
