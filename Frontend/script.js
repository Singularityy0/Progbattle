let currentUser = null;
let currentTeam = null;


const navLinks = document.querySelectorAll('.nav-links a');
const pages = document.querySelectorAll('.page');
const authTabs = document.querySelectorAll('.auth-tab');
const authForms = document.querySelectorAll('.auth-form');
const leaderboardTabs = document.querySelectorAll('.leaderboard-tab');


const loadingOverlay = document.createElement('div');
loadingOverlay.className = 'loading-overlay';
loadingOverlay.innerHTML = '<div class="loading-spinner">Evaluating bot submission... Please wait...</div>';
document.body.appendChild(loadingOverlay);


navLinks.forEach(link => {
    link.addEventListener('click', async (e) => {
        e.preventDefault();
        const page = link.dataset.page;
        if (page) {
            if ((page === 'leaderboard' || page === 'team' || page === 'submit' || page === 'simulations') && !currentUser) {
                showToast('Please login first', 'error');
                await showPage('auth');
                return;
            }
            await showPage(page);
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        }
    });
});


authTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const formId = tab.dataset.tab;
        authTabs.forEach(t => t.classList.remove('active'));
        authForms.forEach(f => f.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(formId + 'Form').classList.add('active');
    });
});

leaderboardTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const round = tab.dataset.round;
        leaderboardTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        loadLeaderboard(round);
    });
});

async function showPage(pageId) {
    pages.forEach(page => page.classList.remove('active'));
    document.getElementById(pageId + 'Page').classList.add('active');

    if (pageId === 'submit' && currentTeam) {
        await loadSubmissionHistory();
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.style.backgroundColor = type === 'success' ? 'var(--secondary-color)' : 'var(--accent-color)';
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}
async function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch('http://localhost:5000/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (response.ok) {            currentUser = { id: data.user_id, username: data.username };
            showToast('Login successful');
            updateAuthState();
            await loadTeams();
            await loadSubmissionHistory();
            showPage('home');
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('An error occurred', 'error');
    }
}

async function register() {
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const response = await fetch('http://localhost:5000/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (response.ok) {
            showToast('Registration successful, please login');
            document.querySelector('[data-tab="login"]').click();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('An error occurred', 'error');
    }
}

function logout() {
    currentUser = null;
    currentTeam = null;
    updateAuthState();
    showPage('home');
}


function updateAuthState() {
    const authLink = document.getElementById('authLink');
    const logoutLink = document.getElementById('logoutLink');
    const teamLink = document.getElementById('teamLink');
    const submitLink = document.getElementById('submitLink');
    const simulationsLink = document.querySelector('[data-page="simulations"]');

    if (currentUser) {
        authLink.style.display = 'none';
        logoutLink.style.display = 'inline-block';
        teamLink.style.display = 'inline-block';
        submitLink.style.display = currentTeam ? 'inline-block' : 'none';
        simulationsLink.style.display = 'inline-block';
    } else {
        authLink.style.display = 'inline-block';
        logoutLink.style.display = 'none';
        teamLink.style.display = 'none';
        submitLink.style.display = 'none';
        simulationsLink.style.display = 'none';
        
        // If on simulations page when logging out, redirect to home
        if (document.getElementById('simulationsPage').classList.contains('active')) {
            showPage('home');
        }
    }
}

// Team functions
async function loadTeams() {
    if (!currentUser) return;

    try {
        const response = await fetch('http://localhost:5000/team/list');
        const teams = await response.json();
        const teamsList = document.getElementById('teamsList');
        const createTeamDiv = document.querySelector('.create-team');

        // Find user's team if any (by searching for currentUser in members)
        let userTeam = null;
        for (const team of teams) {
            if (team.members && team.members.some(member => member.id === currentUser.id)) {
                userTeam = team;
                break;
            }
        }
        currentTeam = userTeam || null;
        createTeamDiv.style.display = currentTeam ? 'none' : 'block';

        teamsList.innerHTML = teams.map(team => {
            const isUserTeam = userTeam && userTeam.id === team.id;
            const teamMembers = team.members || [];
            const isFull = teamMembers.length >= 4;
            return `
                <div class="team-card ${isUserTeam ? 'my-team' : ''}">
                    <h3>${team.name}</h3>
                    <div class="team-details">
                        <p><strong>Members (${teamMembers.length}/4):</strong></p>
                        <div class="team-members">
                            ${teamMembers.length > 0 ? teamMembers.map(member =>
                                `<div class="member ${member.id === currentUser.id ? 'current-user' : ''}">${member.username}</div>`
                            ).join('') : '<div class="member">No members yet</div>'}
                        </div>
                        <p><strong>Round:</strong> ${team.round}</p>
                    </div>
                    ${getTeamActionButton(team, userTeam, isFull)}
                </div>
            `;
        }).join('');

        document.getElementById('submitLink').style.display = currentTeam ? 'inline-block' : 'none';
    } catch (error) {
        showToast('Error loading teams', 'error');
    }
}

function getTeamActionButton(team, userTeam, isFull) {

    if (userTeam && userTeam.id === team.id) {

        if (team.owner_id === currentUser.id) {
            return `<button disabled class="owner-badge">Team Owner</button>`;
        }

        return `
            <button onclick="leaveTeam(${team.id})" class="leave-btn">
                <i class="fas fa-sign-out-alt"></i> Leave Team
            </button>`;
    }
    

    if (userTeam) {
        return '<button disabled>Already in a Team</button>';
    }
    
    // If team is full, show full message
    if (isFull) {
        return '<button disabled>Team Full (4/4)</button>';
    }
    
    // If user is not in any team and team has space, show join button
    return `
        <button onclick="joinTeam(${team.id})" class="join-btn">
            <i class="fas fa-sign-in-alt"></i> Join Team
        </button>`;
}

// Bot submission and history functions
async function submitBot() {
    if (!currentTeam) {
        showToast('Please join a team first', 'error');
        return;
    }

    const fileInput = document.getElementById('botFile');
    if (!fileInput.files.length) {
        showToast('Please select a file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('bot_file', fileInput.files[0]);  // Changed from 'file' to 'bot_file'
    formData.append('team_id', currentTeam.id);

    try {
        loadingOverlay.style.display = 'flex';
        
        const response = await fetch('http://localhost:5000/bot/submit', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            showToast('Bot submitted successfully!');
            fileInput.value = ''; // Clear the file input
            
            // Update UI with match results
            document.getElementById('submissionsList').innerHTML = `
                <div class="submission-card">
                    <div class="submission-header">
                        <h4>Match Results</h4>
                        <div class="score-details">
                            <p>Your Score: ${data.your_score}</p>
                            <p>System Score: ${data.system_score}</p>
                            <p>Final Score: ${data.final_score}</p>
                            <p>Matches Remaining: ${data.matches_remaining}</p>
                        </div>
                    </div>
                    <div class="match-actions">
                        <a href="http://localhost:5000/bot/logs/${data.log_file}" 
                           class="download-btn" target="_blank">
                           <i class="fas fa-download"></i> View Match Log
                        </a>
                    </div>
                </div>
            `;
            
            // Refresh history and leaderboard
            await loadSubmissionHistory();
            await loadLeaderboard(currentTeam.round || 1);
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        console.error('Error submitting bot:', error);
        showToast('An error occurred while submitting your bot', 'error');
    } finally {
        loadingOverlay.style.display = 'none';
    }
}

async function createTeam() {
    if (currentTeam) {
        showToast('You must leave your current team before creating a new one', 'error');
        return;
    }

    const teamName = document.getElementById('teamName').value;
    if (!teamName.trim()) {
        showToast('Please enter a team name', 'error');
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/team/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ team_name: teamName, user_id: currentUser.id })
        });

        const data = await response.json();
        if (response.ok) {
            showToast('Team created successfully');
            document.getElementById('teamName').value = '';
            
            // Set current team immediately to prevent race conditions
            currentTeam = {
                id: data.team_id,
                name: teamName,
                members: [currentUser],
                owner_id: currentUser.id
            };
            
            // Reload teams to get the latest state
            await loadTeams();
            updateAuthState();
            // Show the team page
            showPage('team');
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('An error occurred', 'error');
    }
}

async function joinTeam(teamId) {
    if (currentTeam) {
        showToast('You must leave your current team before joining another', 'error');
        return;
    }

    try {
        const response = await fetch(`http://localhost:5000/team/join/${teamId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUser.id })
        });

        const data = await response.json();        if (response.ok) {
            showToast('Successfully joined team');
            await loadTeams(); // Always reload teams after action
            updateAuthState();
            await loadSubmissionHistory(); // Load team's submission history
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('An error occurred', 'error');
    }
}

async function leaveTeam(teamId) {
    if (!confirm('Are you sure you want to leave this team?')) {
        return;
    }

    try {
        const response = await fetch(`http://localhost:5000/team/leave/${teamId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUser.id })
        });

        const data = await response.json();
        if (response.ok) {
            showToast('Successfully left team');
            await loadTeams(); // Always reload teams after action
            updateAuthState();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('An error occurred', 'error');
    }
}

async function loadSubmissionHistory() {
    if (!currentTeam) return;

    try {
        const response = await fetch(`http://localhost:5000/bot/history/${currentTeam.id}`);
        const submissions = await response.json();
        const submissionsList = document.getElementById('submissionsList');
        
        submissionsList.innerHTML = '';
        
        if (submissions.length === 0) {
            submissionsList.innerHTML = '<p class="no-submissions">No submissions yet</p>';
            return;
        }
        
        submissions.forEach(sub => {
            const submissionDiv = document.createElement('div');
            submissionDiv.className = 'submission-card';
            const dateStr = new Date(sub.timestamp).toLocaleString();
            
            submissionDiv.innerHTML = `
                <div class="submission-header">
                    <h4>Match Results</h4>
                    <div class="score-details">
                        <p>Final Score: ${sub.score}</p>
                        <p>Date: ${dateStr}</p>
                        <p>Round: ${sub.round}</p>
                    </div>
                </div>
                ${sub.logs.length > 0 ? `
                    <div class="match-actions">
                        <a href="http://localhost:5000/bot/logs/${sub.logs[0]}" 
                           class="download-btn" target="_blank">
                           <i class="fas fa-download"></i> View Match Log
                        </a>
                    </div>
                ` : ''}
            `;            submissionsList.appendChild(submissionDiv);
        });
    } catch (error) {
        console.error('Error loading submission history:', error);
        showToast('Error loading submission history', 'error');
    }
}

// Leaderboard
async function loadLeaderboard(round) {
    try {
        const response = await fetch(`http://localhost:5000/leaderboard/round/${round}`);
        const leaderboard = await response.json();
        
        // Update tournament status
        const statusDiv = document.querySelector('.tournament-status');
        if (round === 1) {
            const completedTeams = leaderboard.filter(t => t.matches_played >= 10).length;
            statusDiv.innerHTML = `
                <div class="tournament-progress">
                    <h3>Round 1 Progress</h3>
                    <p>${completedTeams}/24 teams completed their matches</p>
                    <p>${completedTeams >= 24 ? 'Round 1 complete! Top 16 teams have qualified for Round 2.' : 
                       `${24 - completedTeams} more teams needed to complete Round 1`}</p>
                </div>
            `;
        } else {
            statusDiv.innerHTML = '<h3>Round 2 - Top 16 Teams Compete!</h3>';
        }
        
        // Update leaderboard table
        const tbody = document.querySelector('#leaderboardTable tbody');
        tbody.innerHTML = leaderboard.map((entry, index) => {
            let status = '';
            if (round === 1) {
                if (entry.matches_played >= 10) {
                    status = entry.is_qualified ? 
                        '<span class="qualified">Qualified for Round 2! 🏆</span>' : 
                        '<span class="completed">All matches completed</span>';
                } else {
                    status = `${10 - entry.matches_played} matches remaining`;
                }
            }
            
            return `
                <tr class="${entry.is_qualified ? 'qualified' : ''} ${entry.matches_played >= 10 ? 'completed' : ''}">
                    <td>${index + 1}</td>
                    <td>${entry.team_name}</td>
                    <td>${entry.total_score.toFixed(1)}</td>
                    <td>${entry.matches_played}/10</td>
                    <td>${status}</td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        showToast('Error loading leaderboard', 'error');
    }
}

// No submission limits

// Initial setup
document.getElementById('logoutLink').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
});

// Load initial data
loadLeaderboard(1);

// Game Simulation Class
class GameSimulation {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.GRID_SIZE = 30;
        this.CELL_SIZE = this.canvas.width / this.GRID_SIZE;
        this.PADDLE_WIDTH = 2;
        
        this.gameData = [];
        this.currentStep = 0;
        this.isPlaying = false;
        this.animationFrame = null;
        this.lastFrameTime = 0;
        this.speed = 50; // Default speed (50%)
        
        this.setupControls();
    }

    setupControls() {
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.speedSlider = document.getElementById('speedSlider');
        this.speedValue = document.getElementById('speedValue');

        this.playPauseBtn.addEventListener('click', () => {
            this.isPlaying = !this.isPlaying;
            this.playPauseBtn.innerHTML = this.isPlaying ? '<i class="fas fa-pause"></i>' : '<i class="fas fa-play"></i>';
            if (this.isPlaying) this.animate();
        });

        this.resetBtn.addEventListener('click', () => {
            this.currentStep = 0;
            this.updateStats();
            this.render();
        });

        this.speedSlider.addEventListener('input', (e) => {
            this.speed = parseInt(e.target.value);
            this.speedValue.textContent = `${this.speed}%`;
        });
    }

    loadData(csvData) {
        this.gameData = csvData
            .split('\n')
            .slice(1) // Skip header row
            .filter(line => line.trim())
            .map(line => {
                const [step, ball_x, ball_y, paddle1_x, paddle2_x, bot1_action, bot2_action, score_bot1, score_bot2] = line.split(',');
                return {
                    step: parseInt(step),
                    ball: { x: parseFloat(ball_x), y: parseFloat(ball_y) },
                    paddle1: { x: parseFloat(paddle1_x) },
                    paddle2: { x: parseFloat(paddle2_x) },
                    score: { bot1: parseInt(score_bot1), bot2: parseInt(score_bot2) }
                };
            });
        
        this.currentStep = 0;
        this.updateStats();
        this.render();
    }    updateStats() {
        const frame = this.gameData[this.currentStep];
        if (frame) {
            document.getElementById('currentStep').textContent = frame.step;
            const rawScore = `${frame.score.bot1} - ${frame.score.bot2}`;            let finalScore = frame.score.bot1; // Base score
            const isWin = frame.score.bot1 > frame.score.bot2;
            const isClose = Math.abs(frame.score.bot1 - frame.score.bot2) <= 1;
            
            // Apply modifiers
            if (isWin) {
                finalScore += 3;
            } else {
                finalScore = Math.max(0, finalScore - 1);
            }
            if (isClose) finalScore += 1;

            document.getElementById('score').textContent = 
                `${rawScore} (Final: ${finalScore.toFixed(1)}) ${isClose ? '🎯' : ''} ${isWin ? '🏆' : ''}`;
        }
    }

    animate() {
        if (!this.isPlaying || this.currentStep >= this.gameData.length - 1) {
            this.isPlaying = false;
            this.playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
            return;
        }

        const currentTime = performance.now();
        const deltaTime = currentTime - this.lastFrameTime;
        const frameDelay = 1000 / (60 * (this.speed / 50)); // Adjust speed based on slider

        if (deltaTime > frameDelay) {
            this.currentStep++;
            this.updateStats();
            this.render();
            this.lastFrameTime = currentTime;
        }

        requestAnimationFrame(() => this.animate());
    }

    render() {
        const frame = this.gameData[this.currentStep];
        if (!frame) return;

        // Clear canvas
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw ball
        this.ctx.fillStyle = '#fff';
        this.ctx.beginPath();
        this.ctx.arc(
            frame.ball.x * this.CELL_SIZE + this.CELL_SIZE/2,
            frame.ball.y * this.CELL_SIZE + this.CELL_SIZE/2,
            this.CELL_SIZE/2,
            0,
            Math.PI * 2
        );
        this.ctx.fill();        // Draw paddles and labels
        // Player's paddle (bottom)
        this.ctx.fillStyle = '#2196f3';
        this.ctx.fillRect(
            frame.paddle1.x * this.CELL_SIZE,
            (this.GRID_SIZE - 1) * this.CELL_SIZE,
            this.PADDLE_WIDTH * this.CELL_SIZE,
            this.CELL_SIZE
        );
        // Player label
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'left';
        this.ctx.fillText('Your Bot', 10, this.canvas.height - 10);

        // System bot's paddle (top)
        this.ctx.fillStyle = '#f44336';
        this.ctx.fillRect(
            frame.paddle2.x * this.CELL_SIZE,
            0,
            this.PADDLE_WIDTH * this.CELL_SIZE,
            this.CELL_SIZE
        );
        // System bot label
        this.ctx.fillStyle = '#fff';
        this.ctx.fillText('System Bot', 10, 20);

        // Draw grid (optional)
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 0.5;
        for (let i = 0; i <= this.GRID_SIZE; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.CELL_SIZE, 0);
            this.ctx.lineTo(i * this.CELL_SIZE, this.canvas.height);
            this.ctx.stroke();
            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.CELL_SIZE);
            this.ctx.lineTo(this.canvas.width, i * this.CELL_SIZE);
            this.ctx.stroke();
        }
    }
}

// Initialize simulation when DOM is loaded
let gameSimulation;
document.addEventListener('DOMContentLoaded', () => {
    gameSimulation = new GameSimulation();
});

// Function to load simulation from file
async function loadSimulation() {
    const fileInput = document.getElementById('logFile');
    const file = fileInput.files[0];
    if (!file) {
        showToast('Please select a log file', 'error');
        return;
    }

    try {
        const text = await file.text();
        gameSimulation.loadData(text);
        showToast('Simulation loaded successfully', 'success');
    } catch (error) {
        console.error('Error loading simulation:', error);
        showToast('Error loading simulation file', 'error');
    }
}

