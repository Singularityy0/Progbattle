import requests
import random
import time
import string

BASE_URL = "http://localhost:5000"

ADJECTIVES = ['Mighty', 'Swift', 'Clever', 'Brave', 'Epic', 'Dynamic', 'Quantum', 'Cyber', 'Digital', 'Neural']
NOUNS = ['Dragons', 'Phoenix', 'Titans', 'Ninjas', 'Warriors', 'Wizards', 'Hackers', 'Coders', 'Legends', 'Masters']

def generate_username():
    """Generate a random username"""
    prefix = ''.join(random.choice(string.ascii_lowercase) for _ in range(3))
    number = random.randint(100, 999)
    return f"user_{prefix}{number}"

def generate_team_name():
    """Generate a random team name"""
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"

def register_and_login(username, password):
    """Register a new user and then log them in"""
    try:
        # Register
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"username": username, "password": password}
        )
        
        if not register_response.ok:
            print(f"Failed to register {username}: {register_response.json().get('error', 'Unknown error')}")
            return None

        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password}
        )
        
        if not login_response.ok:
            print(f"Failed to login {username}: {login_response.json().get('error', 'Unknown error')}")
            return None

        return login_response.json()
    except Exception as e:
        print(f"Error during registration/login: {str(e)}")
        return None

def create_team(user_id, team_name):
    """Create a new team"""
    try:
        response = requests.post(
            f"{BASE_URL}/team/create",
            json={"team_name": team_name, "user_id": user_id}
        )
        
        if not response.ok:
            print(f"Failed to create team {team_name}: {response.json().get('error', 'Unknown error')}")
            return None

        return response.json()
    except Exception as e:
        print(f"Error creating team: {str(e)}")
        return None

def main():
    # Number of teams to create
    NUM_TEAMS = 20
    
    print(f"Starting automatic setup for {NUM_TEAMS} teams...")
    print("=" * 50)
    
    successful_teams = []
    
    for i in range(NUM_TEAMS):
        # Generate credentials
        username = generate_username()
        password = "test123"  # Simple password for testing
        team_name = generate_team_name()
        
        print(f"\nCreating team {i+1}/{NUM_TEAMS}")
        print(f"Username: {username}")
        print(f"Team name: {team_name}")
        
        # Register and login
        user_data = register_and_login(username, password)
        if not user_data:
            print("Failed to setup user, skipping...")
            continue
            
        user_id = user_data.get('user_id')
        
        # Create team
        team_data = create_team(user_id, team_name)
        if not team_data:
            print("Failed to create team, skipping...")
            continue
            
        successful_teams.append({
            'username': username,
            'password': password,
            'team_name': team_name,
            'user_id': user_id,
            'team_id': team_data.get('team_id')
        })
        
        print(f"Successfully created team {team_name}!")
        
        # Add a small delay to prevent overwhelming the server
        time.sleep(0.5)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Setup completed! Created {len(successful_teams)}/{NUM_TEAMS} teams")
    print("\nTeam Details:")
    print("-" * 50)
    for team in successful_teams:
        print(f"Team: {team['team_name']}")
        print(f"Username: {team['username']}")
        print(f"Password: {team['password']}")
        print(f"Team ID: {team['team_id']}")
        print("-" * 30)
    
    # Save to file
    with open('teams_credentials.txt', 'w') as f:
        f.write("ProgBattle Teams Credentials\n")
        f.write("=" * 50 + "\n\n")
        for team in successful_teams:
            f.write(f"Team: {team['team_name']}\n")
            f.write(f"Username: {team['username']}\n")
            f.write(f"Password: {team['password']}\n")
            f.write(f"Team ID: {team['team_id']}\n")
            f.write("-" * 30 + "\n")

if __name__ == "__main__":
    main() 