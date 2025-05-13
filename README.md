# Project ProgBattle
Escape the Maze with Code  

The World was shattered after the big disaster. The AI systems went down, half of the population was missing and a major part of the technology in the world stopped working. 

The World Governments came together to start **Mission Maze** having the objective of finding the best minds on earth and train them to bring back all the lost information and technology as fast as possible.

You are appointed as the Maze Maker and Selector. To select the best minds on earth you decide to start project ProgBattle which will focus on creating a web portal for hosting a tournament. Where participants will form teams, write intelligent bot scripts, run test battles against system bots, challenge rival teams, and climb the leaderboard in a race to the top.

Only the smartest minds will make it through. Those who reach the final stage will be seen as the best ready to lead Mission Maze and help bring back the lost knowledge and technology.


## You are provided with
1. [`engine.py`](engine.py) it runs the game, you may try one yourself by `python3 engine.py --p1 bot1.py --p2 bot1.py` and creates a [`game_log.csv`](game_log.csv)
2. We have provided you with a basic bot which tries to move in the direction of the ball in the [`bot1.py`](bot1.py)

## Requirements
1. A System for users to login, register using their mail id, [**`Bonus`**: if you can send verification mail :)] create teams [ensure a max size].
2. A publically visible leaderboard
   1. Round one will be based on scores against the system bots provided by the admin. (you may define any scoring system)
   2. Round two will be for the top 16 teams, where they will compete with each others' bot (by system itself and final leaderboard will be published with all the matches in the logs). **`Bonus`** A feature to challenge other teams, this will not be counted for the leaderboard but to improve there strategies.
3. How will the bot-script submitted ?
   1. Any member of the team can login and submit either the code file directly or should be provided a interface to code in the application itself. (no need to provide features like auto completion, background error detection, **but the syntax highlighting is must**)
   2. The user should be able to view his/her team's previous submission, edit them in the application's interface and submit them.
   3. You should ensure that there is a daily / hourly limit for the team / user to submit the scripts.
4. Upon submission:
   1. The Bot should be evaluated against system bots uploaded by the admin, by running the `engine.py` at the server.
   2. The user should be able to see the final scores obtained against the system bots.
   3. Update the global leaderboard accordingly, you may use any scoring strategy.
   4. On user request show the simulations of the game similar to this:
      (you may use any other way to render the simulation, but it should not be a video fetched from backend, it should be rendered using the logs at the frontend itself, `To help you: Research about HTML Canvas`)

      [Simulation video](simulation.mp4)

      <video controls src="simulation.mp4" title="Title" width=300 height= 300></video>
 
   5. **`Bonus`** Check the submission using some sort of plagiarism detector and flag those submissions for the admin.
   6. **`Bonus`** It is possible that the simulation or the evaluation can't be done on the spot due to over load on serve, structure you project to tackle such situations.


## Deliverables 
1. You will be strictly required to submit all your work, research, demo video in a properly documented ( .md files are enough) github repository.
2. A Frontend Interface: Can be very basic in terms of style, as long as it is able to properly demonstrate what you have created. But we don’t mind a full-fledged beautiful frontend :). 
3. All set up instructions should be well described, **`Bonus`** if you can provide us a fully hosted application.
4. Your backend server should be accessible via well-defined endpoint for testing. **`Bonus`** if you properly document how to use the routes using Postman, or any such application.

