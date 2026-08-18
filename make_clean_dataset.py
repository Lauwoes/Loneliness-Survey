"""
Produce a corrected, de-identified version of the loneliness survey data for
publication.

Two changes are made, for two different reasons.

Coding correction
    The five agreement items were reverse-coded the wrong way round. On the
    form, 1 meant strongly disagree and 5 meant strongly agree, so the three
    negatively worded items already point towards loneliness and should be kept
    as recorded; only the two positively worded items need reversing. The
    original file did the opposite, producing a score that measured
    connectedness under a loneliness label.

De-identification
    Age, borough, neighbourhood and occupation together identify individuals in
    a sample of 180, and the outcome being measured is sensitive. Neighbourhood
    and timestamp are removed and age is banded. Borough and occupation are
    broad enough to keep.
"""

from pathlib import Path

import pandas as pd

SRC = Path("/mnt/user-data/uploads/Cleaned_Data_Loneliness_Survey.xlsx")
OUT = Path("/mnt/user-data/outputs")

RC_COLUMNS = {
    "LeftOut_RC": "negative",
    "Companionship_RC": "negative",
    "Isolated_RC": "negative",
    "TalkTo_RC": "positive",
    "Content_RC": "positive",
}

# Age and Specific Area were already blanked in the source file; they are
# dropped rather than carried as empty columns. Timestamp still identifies
# respondents in combination with anything else, so it goes too.
DROP = ["Timestamp", "Specific Area", "Age"]

CODEBOOK = [
    ("Respondent_ID", "Anonymous respondent identifier", "Assigned, not collected"),
    ("NYC Area", "Borough of residence", "Queens is absent from the sample"),
    ("Occupation", "Broad occupation category", "As selected on the form"),
    ("Commute_Flag", "1 if the respondent commutes to work", "Derived"),
    ("Commute_Minutes", "One-way commute in minutes", "Self-reported"),
    ("Long_Commute_Flag", "1 if commute is 45 minutes or longer", "Derived"),
    ("Work_Hours", "Average hours worked per week", "Self-reported"),
    ("Jobs_Count", "Number of jobs currently held", "Self-reported"),
    ("Multi_Job_Flag", "1 if two or more jobs", "Derived"),
    ("PublicSpace_Flag", "1 if the respondent socialises in public spaces", "Derived"),
    ("Live_Alone", "1 if living alone", "Derived from living situation"),
    ("Live_Dorm", "1 if living in a dorm", "Derived from living situation"),
    ("Live_Roommates", "1 if living with roommates", "Derived from living situation"),
    ("Live_Parents", "1 if living with parents", "Derived from living situation"),
    ("LeftOut_RC", "I feel left out", "Kept as recorded; higher = more lonely"),
    ("Companionship_RC", "I lack companionship", "Kept as recorded; higher = more lonely"),
    ("Isolated_RC", "I feel isolated from others", "Kept as recorded; higher = more lonely"),
    ("TalkTo_RC", "I feel there are people I can talk to", "Reverse-coded (6 minus response)"),
    ("Content_RC", "I am content with my friendships and relationships", "Reverse-coded (6 minus response)"),
    ("Loneliness_Score", "Mean of the five items above", "Higher = more lonely. Range 1-5"),
    ("Loneliness_Group", "Low / Moderate / High", "Score under 2.5, 2.5 to 3.5, above 3.5"),
    ("SocialisingHours_Code", "Hours spent socialising per day, coded", "As in original file"),
    ("SocialMedia_Scale", "Hours on social media, coded", "As in original file"),
    ("App_SocialMedia", "1 if social media apps used", "Derived from app list"),
    ("App_Dating", "1 if dating apps used", "Derived from app list"),
    ("App_Therapy", "1 if therapy or companion apps used", "Derived from app list"),
    ("App_Count", "Number of app categories used", "Derived"),
    ("Paid_Service_Flag", "1 if the respondent has paid for a service", "Self-reported"),
    ("Impact_Score", "Perceived impact on loneliness", "Asked of app users only, n = 82"),
    ("Pressure_Score", "Felt pressure to keep paying", "Asked of paying users only"),
    ("Algo_Accuracy_Score", "Perceived matchmaking accuracy", "Asked of app users only"),
    ("Benefits_From_Loneliness_Code", "Believes the app benefits from their loneliness", "Coded response"),
]

NOTES = [
    ("Source", "Original Google Form survey of 180 New York City residents, March 2026"),
    ("Scale direction", "Form used 1 = strongly disagree through 5 = strongly agree"),
    ("Correction applied", "Reverse-coding was inverted in an earlier version of this file. "
                           "The three negatively worded items are now kept as recorded and the "
                           "two positively worded items reversed. Loneliness_Score and "
                           "Loneliness_Group were recomputed."),
    ("Withheld", "Raw responses are not published. Sexual orientation, gender, age, "
                 "timestamp and neighbourhood are excluded, because together they identify "
                 "individuals in a sample of this size."),
    ("Conditional items", "Impact_Score, Pressure_Score and Algo_Accuracy_Score were shown "
                          "only to app users, so each has 82 responses rather than 180. Any "
                          "average from them describes those 82 people."),
    ("Known limitations", "Queens is unrepresented. The sample is self-selected. The design is "
                          "cross-sectional, so no causal direction can be established."),
]


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="Sheet1")

    # The stored _RC columns carry the inverted coding, so recover each item's
    # original response before re-deriving anything from it.
    original = pd.DataFrame(
        {col: 6 - df[col] if kind == "negative" else df[col]
         for col, kind in RC_COLUMNS.items()}
    )

    corrected = pd.DataFrame(
        {col: original[col] if kind == "negative" else 6 - original[col]
         for col, kind in RC_COLUMNS.items()}
    )

    out = df.copy()
    for col in RC_COLUMNS:
        out[col] = corrected[col]

    out["Loneliness_Score"] = corrected.mean(axis=1).round(2)
    out["Loneliness_Group"] = pd.cut(
        out["Loneliness_Score"],
        bins=[0, 2.5, 3.5, 5],
        labels=["Low", "Moderate", "High"],
        include_lowest=True,
    )

    out = out.drop(columns=[c for c in DROP if c in out])

    empty = [c for c in out.columns if out[c].isna().all()]
    if empty:
        raise SystemExit(f"columns are entirely empty, decide before publishing: {empty}")

    csv_path = OUT / "loneliness_survey_clean.csv"
    out.to_csv(csv_path, index=False)

    xlsx_path = OUT / "loneliness_survey_clean.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as xl:
        out.to_excel(xl, sheet_name="Data", index=False)
        pd.DataFrame(CODEBOOK, columns=["Variable", "Description", "Notes"]).to_excel(
            xl, sheet_name="Codebook", index=False
        )
        pd.DataFrame(NOTES, columns=["Item", "Detail"]).to_excel(
            xl, sheet_name="Notes", index=False
        )

    print(f"{len(out)} rows, {len(out.columns)} columns")
    print("dropped:", DROP)
    print("\nscore check, mean by 'I feel left out' response:")
    print(out.groupby(original["LeftOut_RC"])["Loneliness_Score"].mean().round(2).to_string())
    print("\ngroup counts:")
    print(out["Loneliness_Group"].value_counts().to_string())
    print(f"\nwrote {csv_path.name} and {xlsx_path.name}")


if __name__ == "__main__":
    main()
