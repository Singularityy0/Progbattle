# ProgBattle

Escape the Maze with Code

## Project Overview

ProgBattle is a full-stack web application for hosting a programming tournament. Participants form teams, write intelligent bot scripts, compete in matches, and climb the leaderboard. The project features user authentication, team management, bot submission and evaluation, a real-time game engine, and a frontend for match simulation and leaderboard viewing.

## Features

- User registration and login
- cannot view any other page ig not logged in 
- round 1 (functional) and support for round-2 (non functional) :( 
- Team creation, joining, and management (max 4 members per team)
- user can also leave the team as well as long as he/she is not the one who created the team
- Bot script upload and evaluation against system bots
- Real-time use of game engine (`engine.py`) for bot-vs-bot matches
- Scoring system: Win = 5 pts, Draw = 2 pts, Loss = 0 pts, +1 bonus for every 3 goals scored
- Leaderboard with round progression (top 16 teams advance to Round 2)
- Frontend simulation of matches using log files (HTML Canvas)


## Project Structure

```
.
├── server/                # Backend Flask server
│   ├── app.py             # Main app entrypoint
│   ├── models/            # SQLAlchemy models and DB setup
│   ├── routes/            # API endpoints (auth, team, bot, leaderboard)
│   ├── submissions/       # Uploaded bot files
│   └── progbattle_new.db  # SQLite database
├── Frontend/              # HTML/CSS/JS frontend (single-page app)
├── engine.py              # Game engine for bot battles
├── bot1.py                # system bot
├── logs/                  # Game logs (CSV)
├── req.txt                # Python backend dependencies
└── README.md              # Project documentation
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r req.txt
```

### 2. Run the Backend Server

```bash
cd server
python app.py
```

- The server runs on `http://localhost:5000/` by default.

### 3. Run the Game Engine Manually

```bash
python engine.py --p1 bot1.py --p2 bot1.py
```

- Produces `game_log.csv` for simulation.

### 4. Example: Submit a Bot via API

```python
import requests

url = "http://localhost:5000/bot/submit"
files = {'bot_file': open("bot2.py", "rb")}
data = {'team_id': 1}

res = requests.post(url, files=files, data=data)
print(res.json())
```

## WORKINGS
- User first Registers then logins to the server , the username is taken as a unique identity and password is protected using python library werkzeug
- Then they are required to go to the Team section in order to either join a team or create one.
- only after getting a team can user submit a bot , they can only submit 5 bots one by one.
- submission result is shown instantaneously and user is allowed to download the log(csv) file.
- he/she can then use this csv file to view simulation by clicking on the simulation tab
- they can then view leaderboard as well

## Scoring System & Rounds

### Scoring System
- Each time a team submits a bot, it is matched against the system bot (`bot1.py`) using the game engine.
- The scoring for each match is as follows:
  - **Win:** 5 points (if your bot scores more than the system bot)
  - **Draw:** 2 points (if both bots score equally)
  - **Loss:** 0 points (if your bot scores less than the system bot)
  - **Bonus:** +1 point for every 3 goals your bot scores in a match (e.g., 6 goals = +2 bonus)
- The final score for a submission is the sum of the base score (win/draw/loss) and any bonus points.
- After submission, the result (score, log file) is shown instantly, and the user can download the log (CSV) for simulation.

### Submission Limits
- In **Round 1**, each team can submit up to **5 bots** (matches) in total. Only these 5 submissions count towards qualification.

### Round System
- **Round 1:**
  - All teams compete against the system bot.
  - Each team can play up to 5 matches (submissions).
  - The **cumulative score** from these 5 matches determines the team's ranking on the leaderboard.
  - After all teams have played their matches, the top 16 teams (by total score) qualify for Round 2.

- **Round 2:**
  - (Support present, but not fully functional in this version)
  - Qualified teams are intended to compete against each other's bots in a tournament format.
  - The leaderboard for Round 2 would be based on these head-to-head matches.

- The leaderboard can be viewed at any time to see team rankings and qualification status.

## API Endpoints (Summary)

| Endpoint                        | Method | Description                        |
|----------------------------------|--------|------------------------------------|
| `/auth/register`                 | POST   | Register new user                  |
| `/auth/login`                    | POST   | Login user                         |
| `/team/create`                   | POST   | Create a new team                  |
| `/team/join/<team_id>`           | POST   | Join a team                        |
| `/team/leave/<team_id>`          | POST   | Leave a team                       |
| `/team/list`                     | GET    | List all teams                     |
| `/bot/submit`                    | POST   | Submit a bot file                  |
| `/bot/history/<team_id>`         | GET    | Get submission history             |
| `/bot/logs/<filename>`           | GET    | Download game log                  |
| `/leaderboard/`                  | GET    | Get overall leaderboard            |
| `/leaderboard/round/<round_num>` | GET    | Get leaderboard for a round        |
| `/leaderboard/qualify-round-2`   | POST   | Advance top 16 teams to round 2    |
| `/static/<filename>`             | GET    | Download static log files          |

## Example Backend Commands (using `curl`)

### 1. Register a New User

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### 2. Login

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### 3. Create a Team

```bash
curl -X POST http://localhost:5000/team/create \
  -H "Content-Type: application/json" \
  -d '{"team_name": "YourTeamName", "user_id": USER_ID}'
```
> Replace `USER_ID` with the ID returned from the login/register response.

### 4. Join a Team

```bash
curl -X POST http://localhost:5000/team/join/TEAM_ID \
  -H "Content-Type: application/json" \
  -d '{"user_id": USER_ID}'
```
> Replace `TEAM_ID` with the team you want to join and `USER_ID` with your user ID.

### 5. Leave a Team

```bash
curl -X POST http://localhost:5000/team/leave/TEAM_ID \
  -H "Content-Type: application/json" \
  -d '{"user_id": USER_ID}'
```

### 6. List All Teams

```bash
curl http://localhost:5000/team/list
```

### 7. Submit a Bot

```bash
curl -X POST http://localhost:5000/bot/submit \
  -F "bot_file=@path/to/your_bot.py" \
  -F "team_id=TEAM_ID"
```
> Replace `path/to/your_bot.py` with your bot file path and `TEAM_ID` with your team ID.

---

All endpoints return JSON responses. You can also use tools like Postman for easier API testing.

## Database

The backend uses **SQLite** (file: `progbattle_new.db`) with SQLAlchemy ORM for data management. The database is responsible for storing users, teams, and bot submissions, and managing their relationships.

### Main Tables & Relationships

#### 1. **User**
- `id`: Integer, primary key
- `username`: String, unique
- `password_hash`: String
- **Relationships:**
  - Can belong to multiple teams (via association table)
  - Can own a team

#### 2. **Team**
- `id`: Integer, primary key
- `name`: String, unique
- `owner_id`: Foreign key to User
- `max_size`: Integer (default 4)
- `round`: Integer (1 or 2)
- `matches_played`: Integer
- `is_qualified`: Boolean (for round 2)
- `created_at`: DateTime
- **Relationships:**
  - Has multiple members (users)
  - Has multiple submissions

#### 3. **Submission**
- `id`: Integer, primary key
- `team_id`: Foreign key to Team
- `bot_path`: String (file path to uploaded bot)
- `score`: Integer (match score)
- `log_path`: String (file path to match log)
- `timestamp`: DateTime
- `round`: Integer (1 or 2)

#### 4. **team_members** (Association Table)
- Links users and teams (many-to-many relationship)

### How It Works

- When a user registers, a new `User` record is created.
- When a team is created, the creator becomes the owner and is added to the team.
- Users can join/leave teams (unless they are the owner).
- When a bot is submitted, a new `Submission` is created, linked to the team.
- The leaderboard and round progression are calculated from the `Submission` scores.

### Database Initialization

- Tables are created automatically on first run.
- No manual migration is needed for SQLite in development.

### User Authentication & Password Security

- **Username:**
  - Usernames are unique and stored as plain text in the database.

- **Password Storage:**
  - Passwords are **never stored in plain text**.
  - When a user registers, their password is hashed using Werkzeug's secure password hashing utilities (`generate_password_hash`).
  - Only the resulting hash is stored in the `password_hash` field of the `User` table.

- **Password Verification:**
  - During login, the submitted password is checked against the stored hash using `check_password_hash`.
  - This ensures that even if the database is compromised, raw passwords are not exposed.

## Note 
- I tried deploying the website to https://progbattle.onrender.com/ but I dont know how to fix this , for some reason it shows "an error occured" when I try to Register
- maybe it's not able to create the database or something




