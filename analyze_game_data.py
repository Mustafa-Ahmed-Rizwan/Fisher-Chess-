# -*- coding: utf-8 -*-
"""
Analyzes Chess960 game data to compute AI win rate and average decision time.
Reads from game_data.csv and outputs summary statistics.
"""

import pandas as pd

def analyze_game_data(csv_file="game_data.csv"):
    """
    Analyzes game data from the CSV file and prints summary statistics.
    Args:
        csv_file (str): Path to the CSV file containing game data.
    """
    try:
        # Read CSV file with correct column names
        df = pd.read_csv(csv_file, 
                        names=['game_id', 'outcome', 'winner', 'move_count', 'avg_decision_time', 'starting_position', 'timestamp'],
                        sep=',')  # Simple comma separator
        
        # Total number of games
        total_games = len(df)
        
        # Filter completed games (no need for string extraction)
        completed_games = df[df['outcome'].notna()]
        total_completed = len(completed_games)
        
        if total_completed == 0:
            print("No completed games found in the data.")
            return
        
        # AI win rate
        ai_wins = len(completed_games[completed_games['winner'] == "Computer"])
        ai_win_rate = (ai_wins / total_completed) * 100 if total_completed > 0 else 0.0
        
        # Average decision time
        avg_decision_time = completed_games['avg_decision_time'].mean()
        
        # Outcome distribution
        outcome_counts = completed_games['outcome'].value_counts()
        
        # Print summary
        print("\n=== Chess960 AI Performance Report ===")
        print(f"Total Games: {total_games}")
        print(f"Completed Games: {total_completed}")
        print(f"AI Win Rate: {ai_win_rate:.2f}% ({ai_wins}/{total_completed} wins)")
        print(f"Average Decision Time: {avg_decision_time:.4f} seconds")
        print("\nOutcome Distribution:")
        for outcome, count in outcome_counts.items():
            print(f"  {outcome}: {count} ({(count/total_completed)*100:.2f}%)")
        print("\n=====================================")

        # Create summary text
        summary = []
        summary.append("=== Chess960 AI Performance Report ===")
        summary.append(f"Total Games: {total_games}")
        summary.append(f"Completed Games: {total_completed}")
        summary.append(f"AI Win Rate: {ai_win_rate:.2f}% ({ai_wins}/{total_completed} wins)")
        summary.append(f"Average Decision Time: {avg_decision_time:.4f} seconds")
        summary.append("\nOutcome Distribution:")
        for outcome, count in outcome_counts.items():
            summary.append(f"  {outcome}: {count} ({(count/total_completed)*100:.2f}%)")
        summary.append("=====================================")
        
        # Print to console
        print("\n".join(summary))
        
        # Save to file
        output_file = "chess960_ai_report.txt"  # Define the output file path
        with open(output_file, 'w') as f:
            f.write("\n".join(summary))
        print(f"\nReport saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: {csv_file} not found. Please run the game to generate data.")
    except Exception as e:
        print(f"Error analyzing data: {str(e)}")
        print("\nRaw file contents:")
        with open(csv_file, 'r') as f:
            print(f.read())

if __name__ == "__main__":
    analyze_game_data()