import requests
import random
import time
import json

BASE_URL = "http://localhost:5000"

# Available bot files to choose from
BOT_FILES = ['bot1.py', 'bot2.py', 'bot3.py', 'bot4.py', 'bot5.py']

def login_user(username, password):
    """Login a user and return the user data"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.ok:
            return response.json()
        else:
            print(f"Failed to login {username}: {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return None

def get_submission_history(team_id):
    """Get the number of submissions a team has made"""
    try:
        response = requests.get(f"{BASE_URL}/bot/history/{team_id}")
        if response.ok:
            submissions = response.json()
            return len(submissions)
        return 0
    except Exception as e:
        print(f"Error getting submission history: {str(e)}")
        return 0

def submit_bot(team_id, bot_file):
    """Submit a bot for a team"""
    try:
        # Create the form data with the bot file
        files = {'bot_file': open(bot_file, 'rb')}
        data = {'team_id': team_id}
        
        response = requests.post(
            f"{BASE_URL}/bot/submit",
            files=files,
            data=data
        )
        
        if response.ok:
            result = response.json()
            print(f"Bot submission successful!")
            print(f"Your Score: {result.get('your_score', 'N/A')}")
            print(f"System Score: {result.get('system_score', 'N/A')}")
            print(f"Final Score: {result.get('final_score', 'N/A')}")
            return True
        else:
            print(f"Failed to submit bot: {response.json().get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"Error submitting bot: {str(e)}")
        return False
    finally:
        # Make sure to close the file
        files['bot_file'].close()

def main():
    try:
        # Read team credentials from the file
        with open('teams_credentials.txt', 'r') as f:
            content = f.read()
        
        # Parse the credentials file
        teams = []
        current_team = {}
        
        for line in content.split('\n'):
            if line.startswith('Team: '):
                if current_team:
                    teams.append(current_team)
                current_team = {}
                current_team['team_name'] = line.replace('Team: ', '')
            elif line.startswith('Username: '):
                current_team['username'] = line.replace('Username: ', '')
            elif line.startswith('Password: '):
                current_team['password'] = line.replace('Password: ', '')
            elif line.startswith('Team ID: '):
                current_team['team_id'] = int(line.replace('Team ID: ', ''))
        
        if current_team:
            teams.append(current_team)
        
        print(f"Found {len(teams)} teams in credentials file")
        print("=" * 50)
        
        # Process each team
        for team in teams:
            print(f"\nProcessing team: {team['team_name']}")
            
            # Login as team owner
            user_data = login_user(team['username'], team['password'])
            if not user_data:
                print("Failed to login, skipping team...")
                continue
            
            # Check current submission count
            submissions_count = get_submission_history(team['team_id'])
            submissions_needed = 5 - submissions_count
            
            print(f"Current submissions: {submissions_count}")
            print(f"Submissions needed: {submissions_needed}")
            
            # Submit bots if needed
            for i in range(submissions_needed):
                if submissions_needed <= 0:
                    print("No more submissions needed")
                    break
                
                # Choose a random bot file
                bot_file = random.choice(BOT_FILES)
                print(f"\nSubmitting bot {i+1}/{submissions_needed} (using {bot_file})")
                
                # Submit the bot
                success = submit_bot(team['team_id'], bot_file)
                
                if success:
                    print(f"Successfully submitted bot {i+1}")
                else:
                    print(f"Failed to submit bot {i+1}")
                
                # Add a delay between submissions
                time.sleep(1)
            
            print(f"Completed processing team: {team['team_name']}")
            print("-" * 30)
            
            # Add a delay between teams
            time.sleep(0.5)
        
        print("\nBot submission process completed!")
        print("=" * 50)
        
    except FileNotFoundError:
        print("Error: teams_credentials.txt not found!")
        print("Please run auto_setup.py first to create teams and generate credentials.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 