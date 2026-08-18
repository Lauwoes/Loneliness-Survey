# NYC Loneliness Survey

A survey of 180 New York City residents testing whether longer commutes and
multiple jobs go with higher loneliness.

**[View the dashboard →](https://lauwoes.github.io/Loneliness-Survey/loneliness_dashboard.html)**

## The finding

They don't. The relationship runs the other way, and strongly.

Respondents with commutes of 45 minutes or more scored 2.96 on a five-point
loneliness scale against 4.15 for those with shorter commutes. Respondents
holding two or more jobs scored 1.98 against 4.08 for those with one. Both
differences are large and hold up when commute time, work hours, job count,
social media use, living situation and age are entered into a regression
together (R² = 0.72, all four pressure variables significant, VIFs below 3).

Socialising in public spaces goes with *more* loneliness, not less: 4.03
against 3.09.

I predicted the opposite of all of this.

## A coding error hid it

The five agreement items were originally reverse-coded the wrong way round.

The form used 1 for strongly disagree through 5 for strongly agree. The three
negatively worded items ("I feel left out", "I lack companionship", "I feel
isolated from others") already point towards loneliness and should be kept as
recorded. The two positively worded items ("I feel there are people I can talk
to", "I am content with my friendships and relationships") are the ones needing
reversal. The first version of the analysis did the opposite.

The result was a score that measured connectedness while being labelled
loneliness. Respondents giving the most lonely possible answer on "I feel left
out" scored 1.35; those giving the least lonely answer scored 4.58.

Every group difference therefore reported the wrong direction. The data was
never wrong, only one step in how it was scored. The dashboard has a toggle
that switches between the two codings so the effect is visible.

## Method

- 180 responses collected via Google Form, March 2026
- Loneliness measured with five UCLA-style items, scored 1 to 5
- Score is the mean of the five items after correct reverse-coding
- Group differences tested with Welch's t-test; effect sizes are Cohen's d
- Multivariable OLS regression to separate the correlated predictors

## Files

| File | What it is |
| --- | --- |
| `loneliness_dashboard.html` | Interactive dashboard with the coding toggle |
| `loneliness_survey_clean.csv` | De-identified respondent-level data, 180 rows |
| `make_clean_dataset.py` | Script producing the clean file from the source |

## Limitations

**The effect sizes are too large to take at face value.** A Cohen's d of 2.73
for multiple jobs means the two groups barely overlap. Published loneliness
research typically finds correlations between 0.1 and 0.3; several here exceed
0.7. I don't have an explanation for this and would not present it as a
population effect without knowing more.

**The scale may be measuring one thing five times.** Cronbach's alpha is 0.947
with inter-item correlations from 0.73 to 0.83, which usually indicates
near-duplicate items rather than an excellent scale.

**No causal direction can be established.** The design is cross-sectional.
Working more jobs may reduce loneliness, or less lonely people may take on more
work. Nothing here distinguishes them.

**Sampling is self-selected and Queens is absent.** Roughly 2.3 million
residents are unrepresented.

**Some items have smaller bases.** Perceived impact, payment pressure and
matchmaking accuracy were shown only to app users, so each covers 82
respondents rather than 180.

## Data

Raw responses are not published. Sexual orientation, gender, age, timestamp and
neighbourhood are excluded, because together they would identify individuals in
a sample of this size, and the outcome measured is sensitive. Borough and
occupation are broad enough to keep. `make_clean_dataset.py` shows exactly what
was removed.

Coursework for a Statistics with SPSS
