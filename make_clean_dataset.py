"""
Produce the corrected, de-identified loneliness dataset for publication.

Scoring
    The form used 1 for strongly disagree through 5 for strongly agree. Three
    items were worded negatively and two positively, so as recorded they point
    in opposite directions and cancel each other out in an average.

    All five are therefore stored under negative wording, so that a high value
    always means more loneliness. For the two positively worded items that
    means reversing the response, which is the same operation as rewriting the
    statement in the negative: someone who strongly disagreed that people are
    there to talk to strongly agrees that nobody is. Reversing and renaming are
    one step, not two.

    Loneliness_Score is the unweighted mean of the five, so each item counts
    equally.

De-identification
    Age, borough, neighbourhood and occupation together identify individuals in
    a sample of 180, and the outcome is sensitive. Neighbourhood and timestamp
    are removed. Age and neighbourhood were already blank in the source.
"""

from pathlib import Path

import pandas as pd

SRC = Path("/mnt/user-data/uploads/Cleaned_Data_Loneliness_Survey.xlsx")
OUT = Path("/mnt/user-data/outputs")

# The source file stores the five items with the reversal applied the wrong way
# round. Recovering each respondent's actual answer comes first.
STORED = {
    "LeftOut_RC": ("LeftOut", True),                          # stored reversed, should not be
    "Companionship_RC": ("LackCompanionship", True),
    "Isolated_RC": ("Isolated", True),
    "TalkTo_RC": ("NoOneToTalkTo", False),                    # stored as asked, needs reversing
    "Content_RC": ("NotContentWithRelationships", False),
}

MEANING = {
    "LeftOut": "I feel left out",
    "LackCompanionship": "I lack companionship",
    "Isolated": "I feel isolated from others",
    "NoOneToTalkTo": "I feel there is no one I can talk to",
    "NotContentWithRelationships": "I am not content with my friendships and relationships",
}

DROP = ["Timestamp", "Specific Area", "Age"]

CODEBOOK = [
    ("Respondent_ID", "Anonymous respondent identifier", "Assigned, not collected"),
    ("NYC Area", "Borough of residence", "Queens is absent from the sample"),
    ("Occupation", "Broad occupation category", "As selected on the form"),
    ("Commute_Flag", "Commutes to work", "1 = yes"),
    ("Commute_Minutes", "One-way commute in minutes", "Self-reported"),
    ("Long_Commute_Flag", "Commute of 45 minutes or more", "1 = yes"),
    ("Work_Hours", "Average hours worked per week", "Self-reported"),
    ("Jobs_Count", "Number of jobs held", "Self-reported"),
    ("Multi_Job_Flag", "Holds two or more jobs", "1 = yes"),
    ("PublicSpace_Flag", "Socialises in public spaces", "1 = yes"),
    ("Live_Alone", "Lives alone", "1 = yes"),
    ("Live_Dorm", "Lives in a dorm", "1 = yes"),
    ("Live_Roommates", "Lives with roommates", "1 = yes"),
    ("Live_Parents", "Lives with parents", "1 = yes"),
    ("LeftOut", MEANING["LeftOut"], "1-5, as recorded"),
    ("LackCompanionship", MEANING["LackCompanionship"], "1-5, as recorded"),
    ("Isolated", MEANING["Isolated"], "1-5, as recorded"),
    ("NoOneToTalkTo", MEANING["NoOneToTalkTo"],
     "1-5, reversed from 'I feel there are people I can talk to'"),
    ("NotContentWithRelationships", MEANING["NotContentWithRelationships"],
     "1-5, reversed from 'I am content with my friendships and relationships'"),
    ("Loneliness_Score", "Unweighted mean of the five items above",
     "1-5, higher means more lonely"),
    ("Loneliness_Group", "Low / Moderate / High", "Under 2.5 / 2.5-3.5 / above 3.5"),
    ("SocialisingHours_Code", "Hours socialising per day, coded", "As in source"),
    ("SocialMedia_Scale", "Hours on social media, coded", "As in source"),
    ("App_SocialMedia", "Uses social media apps", "1 = yes"),
    ("App_Dating", "Uses dating apps", "1 = yes"),
    ("App_Therapy", "Uses therapy or companion apps", "1 = yes"),
    ("App_Count", "Number of app categories used", "Derived"),
    ("Paid_Service_Flag", "Has paid for a service", "1 = yes"),
    ("Impact_Score", "Perceived impact on loneliness", "App users only, n = 82"),
    ("Pressure_Score", "Felt pressure to keep paying", "Paying users only"),
    ("Algo_Accuracy_Score", "Perceived matchmaking accuracy", "App users only"),
    ("Benefits_From_Loneliness_Code", "Believes the app benefits from their loneliness",
     "Coded response"),
]

NOTES = [
    ("Source", "Google Form survey of 180 New York City residents, March 2026"),
    ("Scale", "1 = strongly disagree through 5 = strongly agree"),
    ("Item direction", "All five items are stored under negative wording so that a high "
                       "value always means more loneliness. The two originally positive "
                       "items were reversed once; respondents were shown the positive "
                       "wording."),
    ("Weighting", "Loneliness_Score is an unweighted mean, so each of the five items "
                  "contributes equally."),
    ("Withheld", "Raw responses are not published. Sexual orientation, gender, age, "
                 "timestamp and neighbourhood are excluded, because together they would "
                 "identify individuals in a sample of this size."),
    ("Conditional items", "Impact_Score, Pressure_Score and Algo_Accuracy_Score were shown "
                          "only to app users, so each covers 82 respondents."),
    ("Limitations", "Queens is unrepresented, the sample is self-selected, and the design "
                    "is cross-sectional so no causal direction can be established."),
]


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="Sheet1")

    # Recover each respondent's actual answer, then apply the correct direction.
    coded = pd.DataFrame(index=df.index)
    for stored_col, (new_name, was_reversed) in STORED.items():
        as_answered = 6 - df[stored_col] if was_reversed else df[stored_col]
        # Negative items keep the answer; positive items are reversed once.
        coded[new_name] = as_answered if was_reversed else 6 - as_answered

    out = df.drop(columns=list(STORED) + [c for c in DROP if c in df])
    insert_at = out.columns.get_loc("Loneliness_Score")
    for offset, name in enumerate(coded.columns):
        out.insert(insert_at + offset, name, coded[name])

    out["Loneliness_Score"] = coded.mean(axis=1).round(2)
    out["Loneliness_Group"] = pd.cut(
        out["Loneliness_Score"], bins=[0, 2.5, 3.5, 5],
        labels=["Low", "Moderate", "High"], include_lowest=True,
    ).astype(str)

    empty = [c for c in out.columns if out[c].isna().all()]
    if empty:
        raise SystemExit(f"columns are entirely empty, decide before publishing: {empty}")

    out.to_csv(OUT / "loneliness_survey_clean.csv", index=False)
    with pd.ExcelWriter(OUT / "loneliness_survey_clean.xlsx", engine="openpyxl") as xl:
        out.to_excel(xl, sheet_name="Data", index=False)
        pd.DataFrame(CODEBOOK, columns=["Variable", "Meaning", "Scoring"]).to_excel(
            xl, sheet_name="Codebook", index=False)
        pd.DataFrame(NOTES, columns=["Item", "Detail"]).to_excel(
            xl, sheet_name="Notes", index=False)

    print(f"{len(out)} rows, {len(out.columns)} columns")
    print("\nmean score by each item's answer (all should increase):")
    for name in coded.columns:
        means = out.groupby(coded[name])["Loneliness_Score"].mean().round(2)
        ok = means.is_monotonic_increasing
        print(f"  {name:30s} {'rising' if ok else 'NOT RISING'}  {list(means.values)}")
        assert ok, f"{name} runs against the score"
    print("\ngroup counts:")
    print(out["Loneliness_Group"].value_counts().to_string())


if __name__ == "__main__":
    main()
