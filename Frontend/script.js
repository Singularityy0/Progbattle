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
            if ((page === 'leaderboard' || page === 'team' || page === 'submit') && !currentUser) {
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

    if (currentUser) {
        authLink.style.display = 'none';
        logoutLink.style.display = 'inline-block';
        teamLink.style.display = 'inline-block';
        submitLink.style.display = currentTeam ? 'inline-block' : 'none';
    } else {
        authLink.style.display = 'inline-block';
        logoutLink.style.display = 'none';
        teamLink.style.display = 'none';
        submitLink.style.display = 'none';
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
    if (submissionLimits.hourly.remaining <= 0) {
        showToast('Hourly submission limit reached. Please wait for the next hour to submit again.', 'error');
        return;
    }

    const fileInput = document.getElementById('botFile');
    if (!fileInput.files.length) {
        showToast('Please select a file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('team_id', currentTeam.id);

    try {
        loadingOverlay.style.display = 'flex';
        
        const response = await fetch('http://localhost:5000/bot/submit', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            const result = data.match_result;
            const wonMessage = result.won ? '🏆 Your bot won!' : '😔 System bot won';
            showToast(`Match completed - ${wonMessage}`);
            
            // Add match results to history
            const submissionsList = document.getElementById('submissionsList');
            const submissionDiv = document.createElement('div');
            submissionDiv.className = 'submission-card';
            submissionDiv.innerHTML = `
                <div class="submission-header">
                    <h4>${wonMessage}</h4>
                    <div class="score-details">
                        <p>Match Points:</p>
                        <p>Your Bot: ${result.your_score} points</p>
                        <p>System Bot: ${result.system_score} points</p>
                        <p class="final-score">Final Score: ${result.final_score} points</p>
                        <p class="score-explanation">${result.won ? 
                            `Winner bonus! Final Score = (${result.your_score} + ${result.system_score})/2 = ${result.final_score}` :
                            `Loss penalty. Final Score = (${result.your_score} - ${result.system_score})/2 = ${result.final_score}`
                        }</p>
                    </div>
                    <p class="match-date">Date: ${new Date().toLocaleString()}</p>
                </div>                <div class="match-actions">
                    
                    <a href="http://localhost:5000/bot/logs/${result.log_file}" 
                       class="download-btn" target="_blank">
                       <i class="fas fa-download"></i> Download Match Log
                    </a>
                </div>
                
            `;
            submissionsList.insertBefore(submissionDiv, submissionsList.firstChild);
            
            // Clear the file input            fileInput.value = '';
            
            // Refresh submission history and leaderboard
            await loadSubmissionHistory();
            await loadLeaderboard(currentTeam.round || 1);
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        showToast('An error occurred', 'error');
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
                        <p>Your Bot's Score: ${sub.score}</p>
                        <p>Date: ${dateStr}</p>
                        <p>Round: ${sub.round}</p>
                    </div>
                </div>                <div class="match-actions">
                    
                    <a href="http://localhost:5000/bot/logs/${sub.logs[0]}" 
                       class="download-btn" target="_blank">
                       <i class="fas fa-download"></i> View Match Log
                    </a>
                </div>
                
            `;
            submissionsList.appendChild(submissionDiv);
        });
        
        // Update submission limits based on history
        updateSubmissionLimits(submissions);
    } catch (error) {
        showToast('Error loading submission history', 'error');
    }
}

// Leaderboard
async function loadLeaderboard(round) {
    try {
        const response = await fetch(`http://localhost:5000/leaderboard/round/${round}`);
        const leaderboard = await response.json();
        const tbody = document.querySelector('#leaderboardTable tbody');
        tbody.innerHTML = leaderboard.map((entry, index) => `
            <tr>
                <td>${index + 1}</td>
                <td>${entry.team_name}</td>
                <td>${entry.total_score}</td>
                <td>${entry.matches_played}</td>
            </tr>
        `).join('');
    } catch (error) {
        showToast('Error loading leaderboard', 'error');
    }
}

// Track submission limits
let submissionLimits = {
    hourly: {
        max: 4,
        remaining: 4,
        resetTime: null
    },
    daily: {
        max: 10,
        remaining: 10,
        resetTime: null
    }
};

function updateSubmissionLimits(submissions) {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const hourStart = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours());
    
    // Count submissions in the last hour and today
    const hourlyCount = submissions.filter(sub => new Date(sub.timestamp) >= hourStart).length;
    const dailyCount = submissions.filter(sub => new Date(sub.timestamp) >= todayStart).length;
    
    // Update remaining counts
    submissionLimits.hourly.remaining = Math.max(0, submissionLimits.hourly.max - hourlyCount);
    submissionLimits.daily.remaining = Math.max(0, submissionLimits.daily.max - dailyCount);
    
    // Calculate next reset times
    const hourlyReset = new Date(hourStart);
    hourlyReset.setHours(hourlyReset.getHours() + 1);
    submissionLimits.hourly.resetTime = hourlyReset;
    
    const dailyReset = new Date(todayStart);
    dailyReset.setDate(dailyReset.getDate() + 1);
    submissionLimits.daily.resetTime = dailyReset;
    
    // Update UI
    updateSubmissionLimitsUI();
}

function updateSubmissionLimitsUI() {
    document.getElementById('hourlySubmissionsLeft').textContent = submissionLimits.hourly.remaining;
    document.getElementById('dailySubmissionsLeft').textContent = submissionLimits.daily.remaining;
    if (submissionLimits.hourly.resetTime) {
        document.getElementById('hourlyResetTime').textContent = submissionLimits.hourly.resetTime.toLocaleTimeString();
    }
    if (submissionLimits.daily.resetTime) {
        document.getElementById('dailyResetTime').textContent = submissionLimits.daily.resetTime.toLocaleTimeString();
    }
    // Disable submit button if hourly limit reached
    const submitBtn = document.querySelector('#submitPage .submission-form button');
    const hourlyNote = document.getElementById('hourlyLimitNote');
    if (submissionLimits.hourly.remaining <= 0) {
        submitBtn.disabled = true;
        hourlyNote.style.display = 'block';
    } else {
        submitBtn.disabled = false;
        hourlyNote.style.display = 'none';
    }
}

// Start timer to update reset times
setInterval(() => {
    if (document.getElementById('submitPage').classList.contains('active')) {
        updateSubmissionLimitsUI();
    }
}, 1000);

// Initial setup
document.getElementById('logoutLink').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
});

// Load initial data
loadLeaderboard(1);

