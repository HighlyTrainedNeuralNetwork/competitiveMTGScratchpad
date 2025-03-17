import numpy as np
from scipy.stats import binom


def calculatePTProbability(baseWinrate=0.55, adjustmentOffset=0.01, targetWins=9):
    day1Rounds = 8
    day1DP = {(0, 0): 1.0}

    for _ in range(day1Rounds):
        newDP = {}
        for (wins, losses), prob in day1DP.items():
            recordOffset = wins - losses
            adjustedWinrate = min(0.99, max(0.01, baseWinrate + (recordOffset * adjustmentOffset)))

            newDP[(wins + 1, losses)] = newDP.get((wins + 1, losses), 0) + prob * adjustedWinrate
            newDP[(wins, losses + 1)] = newDP.get((wins, losses + 1), 0) + prob * (1 - adjustedWinrate)

        day1DP = newDP

    day2Rounds = 8
    finalProbabilities = {}

    for (day1Wins, day1Losses), day1Probability in day1DP.items():
        if day1Wins < 4:
            continue

        day1Offset = day1Wins - day1Losses
        day2DP = {(0, 0): 1.0}

        for _ in range(day2Rounds):
            newDP = {}
            for (day2Wins, day2Losses), day2Probability in day2DP.items():
                recordOffset = day1Offset + (day2Wins - day2Losses)
                adjustedWinrate = min(0.99, max(0.01, baseWinrate + (recordOffset * adjustmentOffset)))

                newDP[(day2Wins + 1, day2Losses)] = newDP.get((day2Wins + 1, day2Losses),
                                                              0) + day2Probability * adjustedWinrate
                newDP[(day2Wins, day2Losses + 1)] = newDP.get((day2Wins, day2Losses + 1), 0) + day2Probability * (
                        1 - adjustedWinrate)

            day2DP = newDP

        for (day2Wins, day2Losses), day2Probability in day2DP.items():
            totalWins = day1Wins + day2Wins
            totalLosses = day1Losses + day2Losses
            record = f"{totalWins}-{totalLosses}"

            finalProbabilities[record] = finalProbabilities.get(record, 0) + day1Probability * day2Probability

    day2Probability = sum(prob for (wins, _), prob in day1DP.items() if wins >= 4)
    targetProbability = sum(prob for record, prob in finalProbabilities.items()
                            if int(record.split("-")[0]) >= targetWins)

    targetRecords = {k: v for k, v in finalProbabilities.items() if int(k.split("-")[0]) >= targetWins}
    sortedRecords = sorted(targetRecords.items(),
                           key=lambda x: (int(x[0].split("-")[0]), -int(x[0].split("-")[1])),
                           reverse=True)

    totalRounds = day1Rounds + day2Rounds
    coinFlip = sum(binom.pmf(k, totalRounds, 0.5) for k in range(targetWins, totalRounds + 1))
    naive = sum(binom.pmf(k, totalRounds, baseWinrate) for k in range(targetWins, totalRounds + 1))

    return {
        "day2Probability": day2Probability,
        "targetProbability": targetProbability,
        "recordProbabilities": sortedRecords,
        "reference": {"coinFlip": coinFlip, "naive": naive}
    }


if __name__ == "__main__":
    baseWinrate = 0.55
    adjustment = 0.01
    targetWins = 9

    results = calculatePTProbability(baseWinrate, adjustment, targetWins)

    print(f"- Base win rate: {baseWinrate * 100:.1f}%")
    print(f"- Win rate adjustment per record offset: {adjustment * 100:.1f}%")
    print(f"- Target wins: {targetWins}+ wins")

    print("\nProbabilities by final record:")
    for record, probability in results["recordProbabilities"]:
        print(f"{record}: {probability * 100:.2f}%")

    print(f"\nProbability of making day 2 (4-4 or better): {results['day2Probability'] * 100:.2f}%")
    print(f"Total probability of {targetWins}-{16 - targetWins} or better: {results['targetProbability'] * 100:.2f}%")

    print(f"\nReference: 50% win rate would give {results['reference']['coinFlip'] * 100:.2f}% chance of {targetWins}+ wins")
    print(f"Reference: {baseWinrate * 100:.1f}% constant win rate would give {results['reference']['naive'] * 100:.2f}% chance of {targetWins}+ wins")