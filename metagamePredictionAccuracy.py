import pandas as pd

# two possible modalities for this.
# 1. we have a percentage prediction for individual players as well as the final deck they played
# 2. we have a prediction about the complete metagame breakdown and the final metagame breakdown
# for now just implement 1

def scorePredictions(playerData):
    """
        Args:
        playerData (dict): dictionary of predictions keys are players
             and the value is a dictionary containing:
             - "actualDeck": The deck the player actually played
             - "predictionOne": tuple of (probability, predicted_deck)
             - "predictionTwo" (optional): tuple of (probability, predicted_deck)
        Returns:
        float: a brier score?
    """
    scores = []
    for player, data in playerData.items():
        probDecimal = float(data["predictionOne"][0]) / 100.0
        outcome = 1 if data["predictionOne"][1] == data["actualDeck"] else 0
        scores.append((probDecimal - outcome) ** 2)
        if "predictionTwo" in data:
            probDecimal = float(data["predictionTwo"][0]) / 100.0
            outcome = 1 if data["predictionTwo"][1] == data["actualDeck"] else 0
            scores.append((probDecimal - outcome) ** 2)
    score = sum(scores) / len(scores)
    return score


if __name__ == "__main__":
    df = pd.read_csv("assets/Pioneer Showcase Scouting 2024 S3 - Scoring.csv")
    unexpected = df["Unexpected Players Present"].dropna().tolist()
    expectedMissing = df["Expected Players Not Present"].dropna().tolist()

    playerData = {}
    for index, row in df.iterrows():
        name = row["Player Name.1"]
        if not pd.isna(name) and name not in unexpected and name not in expectedMissing:
            matchingRow = df[df["Player Name"] == name].iloc[0].squeeze()
            if not pd.isna(matchingRow["Probability #1"]):
                playerData[name] = {"actualDeck": row["Deck"]}
                playerData[name]["predictionOne"] = (matchingRow["Probability #1"], matchingRow["Deck #1"])

                if not pd.isna(matchingRow["Probability #2"]) and matchingRow["Probability #2"] > 0:
                    playerData[name]["predictionTwo"] = (matchingRow["Probability #2"], matchingRow["Deck #2"])


    print(scorePredictions(playerData))