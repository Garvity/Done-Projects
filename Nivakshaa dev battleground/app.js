/* 
    File: app.js
    Minimalist Booking System (Node.js + Express + Vanilla JS + TailwindCSS)
*/

const express = require('express');
const app = express();
const PORT = 3000;

// Find and replace the slots initialization code
const createDaySlots = (date) => {
    return Array.from({ length: 8 }, (_, i) => ({
        time: `${10 + i}:00`,
        date: date,
        booked: false,
        name: null,
        bookedAt: null
    }));
};

// Initialize slots with persistent data structure
const slots = {};

// Initialize for next 5 days starting from tomorrow
(() => {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 1); // Start from tomorrow
    startDate.setHours(0, 0, 0, 0); // Reset time part

    for (let i = 0; i < 5; i++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);
        const dateStr = currentDate.toISOString().split('T')[0];
        slots[dateStr] = createDaySlots(dateStr);
    }
})();

const users = {};

app.use(express.json());


function findUserByEmailOrUsername(email, username) {
    return Object.values(users).find(user => 
        user.email.toLowerCase() === email.toLowerCase() || 
        user.username.toLowerCase() === username.toLowerCase()
    );
}

// Replace the existing authentication endpoint with this updated version
app.post('/auth', (req, res) => {
    const { email, username, password } = req.body;
    
    // Simple validation
    if (!email || !username || !password) {
        return res.json({ success: false, message: "All fields are required." });
    }

    // Check if user exists
    const existingUser = findUserByEmailOrUsername(email, username);
    
    if (existingUser) {
        // If username matches - attempt login
        if (users[username] && users[username].email === email) {
            if (users[username].password !== password) {
                return res.json({ 
                    success: false, 
                    message: "Incorrect password." 
                });
            }
            // Password correct - login successful
            const token = Buffer.from(username).toString('base64');
            return res.json({ success: true, token, username });
        }
        
        // Username or email already exists but doesn't match
        return res.json({ 
            success: false, 
            message: "Email or username already registered. Please try different credentials." 
        });
    }

    // New user - create account
    users[username] = { email, username, password };
    const token = Buffer.from(username).toString('base64');
    res.json({ 
        success: true, 
        token, 
        username,
        message: "Registration successful!" 
    });
});

// Add login route
app.get('/login', (req, res) => {
    res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Booking System</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-blue-100 via-purple-50 to-pink-100 p-8">
        <div class="max-w-md mx-auto bg-white/50 backdrop-blur-sm p-8 rounded-xl shadow-lg">
            <h1 class="text-3xl font-bold mb-6 text-center text-gray-800">Login/Register</h1>
            <form id="authForm" class="space-y-4">
                <div>
                    <label class="block text-gray-700">Email</label>
                    <input type="email" id="email" required class="w-full px-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-purple-500">
                </div>
                <div>
                    <label class="block text-gray-700">Username</label>
                    <input type="text" id="username" required class="w-full px-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-purple-500">
                </div>
                <div class="relative">
                    <label class="block text-gray-700">Password</label>
                    <div class="relative">
                        <input type="password" id="password" required class="w-full px-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-purple-500">
                        <button type="button" id="togglePassword" class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" id="eyeIcon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                        </button>
                    </div>
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 rounded-lg hover:from-blue-600 hover:to-purple-700">
                    Login/Register
                </button>
            </form>
        </div>
        <script>
            document.getElementById('authForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('email').value;
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                try {
                    const response = await fetch('/auth', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, username, password })
                    });
                    const data = await response.json();
                    
                    if (data.success) {
                        localStorage.setItem('userToken', data.token);
                        localStorage.setItem('userName', data.username);
                        window.location.href = '/';
                    } else {
                        alert(data.message);
                    }
                } catch (err) {
                    alert('An error occurred. Please try again.');
                }
            });

            const togglePassword = document.getElementById('togglePassword');
            const password = document.getElementById('password');
            const eyeIcon = document.getElementById('eyeIcon');

            togglePassword.addEventListener('click', function () {
                const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
                password.setAttribute('type', type);
                
                if (type === 'text') {
                    eyeIcon.innerHTML = \`
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    \`;
                } else {
                    eyeIcon.innerHTML = \`
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    \`;
                }
            });
        </script>
    </body>
    </html>
    `);
});

// Serve frontend
app.get('/', (req, res) => {
    res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Minimalist Booking System</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-blue-100 via-purple-50 to-pink-100 p-8">
        <script>
            // Add authentication check
            if (!localStorage.getItem('userToken')) {
                window.location.href = '/login';
            }
        </script>
        <div class="max-w-6xl mx-auto flex flex-col items-center">
            <h1 class="text-4xl font-bold mb-8 text-gray-800 tracking-tight">
                <span class="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                    Booking Slots
                </span>
            </h1>
            
            <div class="text-center mb-6">
                <p class="text-lg text-gray-700">
                    Book your preferred time slot from 
                    <span class="font-semibold text-purple-600">${new Date(Date.now() + 24 * 60 * 60 * 1000).toLocaleDateString()}</span> 
                    to 
                    <span class="font-semibold text-purple-600">${new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toLocaleDateString()}</span>
                </p>
                <p class="text-sm text-gray-500 mt-1">Slots are available from 10:00 AM to 5:00 PM</p>
            </div>
            
            <div id="message" class="mb-6 text-center"></div>
            
            <div class="mb-8 p-4 bg-white/50 backdrop-blur-sm rounded-lg shadow-lg">
                <label for="dateSelect" class="mr-2 font-semibold text-gray-700">Select Date:</label>
                <select id="dateSelect" class="border border-gray-300 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white/70">
                    ${(() => {
                        const dates = [];
                        const startDate = new Date();
                        startDate.setDate(startDate.getDate() + 1); // Start from tomorrow
                        
                        for (let i = 0; i < 5; i++) {
                            const currentDate = new Date(startDate);
                            currentDate.setDate(startDate.getDate() + i);
                            const dateStr = currentDate.toISOString().split('T')[0];
                            dates.push(`
                                <option value="${dateStr}" ${i === 0 ? 'selected' : ''}>
                                    ${currentDate.toLocaleDateString()}
                                </option>
                            `);
                        }
                        return dates.join('');
                    })()}
                </select>
            </div>

            <div id="slots" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8 w-full"></div>
        </div>

        <div class="fixed inset-0 -z-10 bg-[radial-gradient(45rem_50rem_at_top,theme(colors.indigo.100),white)] opacity-50"></div>

        <div class="absolute top-4 right-4">
            <button onclick="logout()" 
                class="bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-2 rounded-md hover:from-red-600 hover:to-red-700">
                Logout
            </button>
        </div>

        <script>
            // Update the fetchSlots function
            function fetchSlots() {
                const selectedDate = document.getElementById('dateSelect').value;
                if (!selectedDate) return;
                
                fetch('/slots/' + selectedDate)
                    .then(res => res.json())
                    .then(data => {
                        if (Array.isArray(data)) {
                            renderSlots(data);
                        }
                    })
                    .catch(err => console.error('Error fetching slots:', err));
            }

            function formatTime(time) {
                const [hours] = time.split(':');
                const hr = parseInt(hours);
                return \`\${hr > 12 ? hr - 12 : hr}:00 \${hr >= 12 ? 'PM' : 'AM'}\`;
            }

            function renderSlots(slots) {
                const container = document.getElementById('slots');
                const currentInputs = Array.from(container.querySelectorAll('input')).reduce((acc, input) => {
                    const form = input.closest('form');
                    if (form) {
                        acc[form.dataset.time] = input.value || ''; // Store empty string if no value
                    }
                    return acc;
                }, {});
                
                container.innerHTML = '';
                slots.forEach(slot => {
                    const isBooked = slot.booked;
                    const slotDiv = document.createElement('div');
                    slotDiv.className = "p-6 rounded-xl shadow-lg flex flex-col items-center justify-between min-h-[200px] transition-all duration-300 transform hover:scale-105 " + 
                        (isBooked 
                            ? "bg-gradient-to-br from-red-50 to-red-100 border border-red-200" 
                            : "bg-gradient-to-br from-green-50 to-green-100 border border-green-200"
                        );
                    
                    // Only use the saved input value for this specific slot
                    const savedValue = currentInputs[slot.time] || '';
                    
                    slotDiv.innerHTML = \`
                        <div class="text-lg font-bold slot-time mb-3 text-gray-800" data-booked="\${isBooked}" data-time="\${slot.time}">
                            \${formatTime(slot.time)}
                        </div>
                        <div class="mb-4 text-center font-medium \${isBooked ? 'text-red-600' : 'text-green-600'}">
                            \${isBooked 
                                ? \`Booked by \${slot.name}<br>
                                   <span class="text-sm text-gray-500 font-normal">
                                       \${new Date(slot.bookedAt).toLocaleString()}
                                   </span>\`
                                : "Available"
                            }
                        </div>
                        \${isBooked 
                            ? \`<button class="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-6 py-2 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg" onclick="cancelSlot('\${slot.time}')">Cancel</button>\`
                            : \`
                                <form onsubmit="bookSlot(event, '\${slot.time}')" data-time="\${slot.time}" class="w-full flex flex-col items-center">
                                    <button class="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-6 py-2 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg w-full font-medium">
                                        Book Now
                                    </button>
                                </form>
                            \`
                        }
                    \`;
                    container.appendChild(slotDiv);
                });
            }

            function bookSlot(e, time) {
                e.preventDefault();
                const username = localStorage.getItem('userName');
                if (!username) {
                    window.location.href = '/login';
                    return;
                }
                const date = document.getElementById('dateSelect').value;
                
                fetch('/book', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ time, date, name: username })
                })
                .then(res => res.json())
                .then((data) => {  // Added missing parentheses here
                    showMessage(data.message, data.success);
                    if (data.success) {
                        fetchSlots();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('An error occurred while booking the slot', false);
                });
            }

            function cancelSlot(time) {
                if (!confirm("Cancel this booking?")) return;
                const date = document.getElementById('dateSelect').value;
                const username = localStorage.getItem('userName');
                
                if (!username) {
                    window.location.href = '/login';
                    return;
                }
                
                fetch('/cancel', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ time, date, username })
                })
                .then(res => res.json())
                .then(data => {
                    showMessage(data.message, data.success);
                    if (data.success) {
                        fetchSlots();
                    }
                });
            }

            function showMessage(msg, success) {
                const el = document.getElementById('message');
                el.textContent = msg;
                el.className = "mb-4 text-center " + (success ? "text-green-700" : "text-red-700");
                setTimeout(() => { el.textContent = ""; }, 2000);
            }

            function logout() {
                localStorage.removeItem('userToken');
                localStorage.removeItem('userName');
                window.location.href = '/login';
            }

            fetchSlots();
            setInterval(fetchSlots, 10000); // Refresh every 10 seconds

            // Add date change event listener
            document.getElementById('dateSelect').addEventListener('change', fetchSlots);
        </script>
    </body>
    </html>
    `);
});

// API: Get all slots
app.get('/slots/:date', (req, res) => {
    const { date } = req.params;
    
    // Ensure the date has slots
    if (!slots[date]) {
        const requestDate = new Date(date);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        // Only create slots for future dates within 5 days
        if (requestDate > today && requestDate <= new Date(today.setDate(today.getDate() + 5))) {
            slots[date] = createDaySlots(date);
        }
    }
    
    // Return slots or empty array if date is invalid
    res.json(slots[date] || []);
});

// API: Book a slot
app.post('/book', (req, res) => {
    const { time, date, name } = req.body;
    const daySlots = slots[date];
    
    if (!daySlots) {
        return res.json({ success: false, message: "Invalid date." });
    }
    
    // Check if user already has a booking for this date
    const existingBooking = daySlots.find(s => s.booked && s.name === name);
    if (existingBooking) {
        return res.json({ 
            success: false, 
            message: "You already have a booking for this date." 
        });
    }
    
    const slot = daySlots.find(s => s.time === time);
    if (!slot) {
        return res.json({ success: false, message: "Invalid time slot." });
    }
    
    if (slot.booked) {
        return res.json({ success: false, message: "This slot is already booked." });
    }
    
    slot.booked = true;
    slot.name = name;
    slot.bookedAt = new Date().toISOString();
    
    res.json({ success: true, message: "Slot booked successfully!" });
});

// API: Cancel a slot
app.post('/cancel', (req, res) => {
    const { time, date, username } = req.body;
    const daySlots = slots[date];
    
    if (!daySlots) {
        return res.json({ success: false, message: "Invalid date." });
    }
    
    const slot = daySlots.find(s => s.time === time);
    if (!slot) {
        return res.json({ success: false, message: "Invalid time slot." });
    }
    
    if (!slot.booked) {
        return res.json({ success: false, message: "This slot is not booked." });
    }

    // Only allow users to cancel their own bookings
    if (slot.name !== username) {
        return res.json({ 
            success: false, 
            message: "You can only cancel your own bookings." 
        });
    }
    
    slot.booked = false;
    slot.name = null;
    slot.bookedAt = null;
    
    res.json({ success: true, message: "Booking cancelled successfully!" });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
