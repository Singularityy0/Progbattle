import requests
import time

BASE_URL = "http://localhost:5000"

def get_leaderboard():
    """Get the current leaderboard data"""
    try:
        response = requests.get(f"{BASE_URL}/leaderboard/round/1")
        if response.ok:
            return response.json()
        print(f"Failed to get leaderboard: {response.json().get('error', 'Unknown error')}")
        return None
    except Exception as e:
        print(f"Error getting leaderboard: {str(e)}")
        return None

def check_all_teams_completed():
    """Check if all teams have completed their 5 submissions"""
    leaderboard = get_leaderboard()
    if not leaderboard:
        return False
    
    total_teams = len(leaderboard)
    completed_teams = len([team for team in leaderboard if team.get('matches_played', 0) >= 5])
    
    print(f"\nTeam Completion Status:")
    print(f"Total Teams: {total_teams}")
    print(f"Teams Completed: {completed_teams}")
    print(f"Teams Pending: {total_teams - completed_teams}")
    
    return completed_teams == total_teams

def qualify_teams():
    """Trigger the qualification process for Round 2"""
    try:
        response = requests.post(f"{BASE_URL}/leaderboard/qualify-round-2")
        if response.ok:
            print("\nQualification process completed successfully!")
            return True
        print(f"Failed to qualify teams: {response.json().get('error', 'Unknown error')}")
        return False
    except Exception as e:
        print(f"Error during qualification: {str(e)}")
        return False

def display_qualified_teams():
    """Display the teams that qualified for Round 2"""
    leaderboard = get_leaderboard()
    if not leaderboard:
        return
    
    print("\nQualified Teams for Round 2:")
    print("=" * 50)
    print(f"{'Rank':<6}{'Team':<30}{'Score':<10}{'Status':<15}")
    print("-" * 50)
    
    for i, team in enumerate(leaderboard[:16], 1):
        status = "✅ Qualified" if team.get('is_qualified') else "❌ Not Qualified"
        print(f"{i:<6}{team['team_name']:<30}{team['total_score']:<10.1f}{status:<15}")

def main():
    print("Checking team completion status...")
    
    # Wait until all teams have completed their submissions
    while not check_all_teams_completed():
        print("\nNot all teams have completed their submissions.")
        print("Waiting 10 seconds before checking again...")
        time.sleep(10)
    
    print("\nAll teams have completed their submissions!")
    print("Starting qualification process...")
    
    # Trigger qualification process
    if qualify_teams():
        # Display final results
        display_qualified_teams()
        
        print("\nQualification process complete!")
        print("You can now proceed with Round 2.")
    else:
        print("\nQualification process failed.")
        print("Please check the server logs for more information.")

if __name__ == "__main__":
    main() 