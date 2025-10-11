console.log("script.js loaded successfully!");


// --------------------- Flight Data Fetching ---------------------
let allFlights = [];
let filteredFlightsShown = []; // Flights after user searched from source → destination
let backupFilteredFlights = [];
let lastSearchedSource = "";
let lastSearchedDestination = "";



window.onload = function () {
    fetch('/flights_json')  
        .then(response => response.json())
        .then(data => {
            allFlights = data;
            console.log("All Flights Loaded:", allFlights);
        })
        .catch(error => console.error('Error fetching flights:', error));

    // Attach real-time filtering listeners
    document.getElementById("alert-price").addEventListener("input", livePriceAlert);
    document.getElementById("alert-flight").addEventListener("input", livePriceAlert);
};  

// --------------------- Real-time Price + Destination Filter ---------------------
function livePriceAlert() {
    const alertPriceInput = document.getElementById("alert-price").value.trim(); 
    const alertPrice = parseFloat(document.getElementById("alert-price").value);
    const message = document.getElementById("alert-message");
    const availableFlightsDiv = document.querySelector(".flights-grid");

    if (isNaN(alertPrice) || alertPrice <= 0) {
        message.textContent = "⚠️ Please enter a valid price.";
        availableFlightsDiv.innerHTML = "";
        return;
    }

    message.textContent = "";
    availableFlightsDiv.innerHTML = "";

    // ✅ Make sure user has searched for flights first
    if (filteredFlightsShown.length === 0) {
        message.textContent = "⚠️ Please search for flights first.";
        return;
    }

    // ✅ Filter only shown flights by price
    const matchingFlights = filteredFlightsShown.filter(flight => Number(flight.price) <= alertPrice);

    // ✅ If no match
    if (matchingFlights.length === 0) {
        message.textContent = `No flights found under ₹${alertPrice}.`;
        return;
    }

    // ✅ Show match message
    message.textContent = `${matchingFlights.length} flights found under ₹${alertPrice}.`;

    // ✅ Re-render only matching flights
    matchingFlights.forEach(flight => {
        const airline = flight.airline || "Unknown Airline";
        const arrivalTimeRaw = flight.arrival_time || "N/A";
        const departureTimeRaw = flight.departure_time || "N/A";
        const arrivalTime = formatTime(arrivalTimeRaw);
        const departureTime = formatTime(departureTimeRaw);
        const flightNumber = flight.flight_number || "N/A";
        const seats = flight.seats_available || "N/A";
        const duration = flight.duration || "N/A";
        const departureDate = formatDate(departureTimeRaw);
        const arrivalDate = formatDate(arrivalTimeRaw);

        let formattedPrice = !isNaN(flight.price)
            ? parseFloat(flight.price).toLocaleString('en-IN', {
                style: 'currency',
                currency: 'INR',
                minimumFractionDigits: 2
            })
            : "₹N/A";

        const classType = flight.flight_class ? flight.flight_class.toLowerCase().replace(/\s+/g, '-') : 'unknown';

        const flightCard = document.createElement('div');
        flightCard.classList.add('flight-card');
        flightCard.innerHTML = `
        <div class="flight-header">
            <h3 class="flight-route">🛫 ${flight.departure} → 🛬 ${flight.arrival}</h3>
            <span class="flight-class-tag ${classType}">${flight.flight_class}</span>
        </div>
        <div class="flight-info">
            <p><strong>✈️ Airline:</strong> ${airline}</p>
            <p><strong>🔢 Flight No:</strong> ${flightNumber}</p>
            <p><strong>🛩️ Aircraft:</strong> ${flight.aircraft || "N/A"}</p>
            <div class="flight-times"> 
                <div class="time">
                    <p>⏰ <strong>Departure:</strong> ${departureTime}</p>
                    <p>📅 <strong>Departure Date:</strong> ${departureDate}</p>
                </div>
                <div class="progress-bar">
                    <div class="line"></div>
                    <div class="dot start"></div>
                    <div class="dot end"></div>
                </div>
                <div class="time">
                    <p>🛬 <strong>Arrival:</strong> ${arrivalTime}</p>
                    <p>📅 <strong>Arrival Date:</strong> ${arrivalDate}</p>
                </div>
            </div>
            <p><strong>🕒 Duration:</strong> ${duration}</p>
            <p><strong>💺 Seats Available:</strong> ${seats}</p>
            <p><strong>💰 Price:</strong> ${formattedPrice}</p>
        </div>
        <a href="/booking/${flight.id}" class="book-btn">Book Now</a>
        `;

        availableFlightsDiv.appendChild(flightCard);
    });
}


// ---------------------Reset Price Alert Functionality ---------------------
function resetPriceAlert() {
    document.getElementById("alert-price").value = "";
    document.getElementById("alert-message").textContent = "";

    if (backupFilteredFlights.length > 0) {
        displayFlightResults(backupFilteredFlights, lastSearchedSource, lastSearchedDestination);
    }
}





// --------------------- Voice Assistant Activation ---------------------
const voiceAssistantBtn = document.getElementById("voice-assistant-btn");

// Initialize Speech Recognition
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = false;
recognition.interimResults = false;
recognition.lang = "en-US";

let isRecognizing = false; // <-- track state

voiceAssistantBtn.addEventListener("click", activateVoiceAssistant);

function activateVoiceAssistant() {
    if (!isRecognizing) {
        alert("Voice Assistant Activated! Speak to search for flights.");
        recognition.start();
        isRecognizing = true;
    } else {
        alert("Voice Assistant is already active.");
    }
}

// Reset the flag when recognition ends
recognition.onend = function () {
    isRecognizing = false;
};


// Handle Speech Recognition Results
recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript.toLowerCase();
    console.log("You said:", transcript);

    // Process the command
    processCommand(transcript);

    // Send command to backend (if needed)
    try {
        const response = await fetch("/run-assistant", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ command: transcript })
        });
        const data = await response.text();
        console.log("Backend Response:", data);
    } catch (error) {
        console.error("Error communicating with backend:", error);
    }
};

// Function to process voice commands
function processCommand(command) {
    // Book a Flight
    if (command.includes("book a flight from")) {
        let match = command.match(/book a flight from (.+) to (.+)/);
        if (match) {
            let source = match[1].trim();
            let destination = match[2].trim();
            speak(`Booking a flight from ${source} to ${destination}.`);

            document.querySelector('input[placeholder="Enter source city"]').value = source;
            document.querySelector('input[placeholder="Enter destination city"]').value = destination;
        } else {
            speak("Please say 'Book a flight from [source] to [destination]'.");
        }
    }

    // Show Flights
    else if (command.includes("show flights from")) {
        let match = command.match(/show flights from (.+) to (.+)/);
        if (match) {
            let source = match[1].trim();
            let destination = match[2].trim();
            speak(`Showing flights from ${source} to ${destination}.`);

            document.querySelector('input[placeholder="Enter source city"]').value = source;
            document.querySelector('input[placeholder="Enter destination city"]').value = destination;
            
            document.querySelector('button[type="submit"], .search-button').click();
        } else {
            speak("Please say 'Show flights from [source] to [destination]'.");
        }
    }

    // Search a Flight
    else if (command.includes("search a flight from")) {
        let match = command.match(/search a flight from (.+) to (.+)/);
        if (match) {
            let source = match[1].trim();
            let destination = match[2].trim();
            speak(`Searching for flights from ${source} to ${destination}.`);

            document.querySelector('input[placeholder="Enter source city"]').value = source;
            document.querySelector('input[placeholder="Enter destination city"]').value = destination;

            document.querySelector('button[type="submit"], .search-button').click();
        } else {
            speak("Please say 'Search a flight from [source] to [destination]'.");
        }
    }

// Filter flights by destination and price
else if (
    command.includes("filter flights") ||
    command.includes("show flights to") ||
    command.includes("find flights to")
) {
    let match = command.match(/(?:filter flights|show flights to|find flights to) (.+) under (\d+)/);
    if (match) {
        let destination = match[1].trim();
        let price = match[2].trim();
        speak(`Filtering flights to ${destination} under ${price} rupees.`);

        // Fill in the destination and price fields
        document.querySelector('input[placeholder="Enter Destination"]').value = destination;
        document.querySelector('input[placeholder="Enter Price"]').value = price;

        // Trigger filter logic (replace selector if needed)
        document.querySelector('button[type="submit"], .filter-button').click();
    } else {
        speak("Please say something like 'show flights to Mumbai under 5000'.");
    }
}


    // Turn on Dark Mode
    else if (command.includes("turn on dark mode")) {
        speak("Turning on dark mode.");
        document.querySelector('input[type="checkbox"]').checked = true;
        document.body.classList.add("dark-mode");
    }

    // Turn off Dark Mode
    else if (command.includes("turn off dark mode")) {
        speak("Turning off dark mode.");
        document.querySelector('input[type="checkbox"]').checked = false;
        document.body.classList.remove("dark-mode");
    }

    // Open My Bookings
    else if (command.includes("open my bookings")) {
        speak("Opening your flight bookings.");
        window.location.href = "/my-bookings"; 
    }

    // If command not recognized
    else {
        speak("Sorry, I didn't understand that.");
    }
}

// Function to simulate speech output
function speak(text) {
    const speech = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(speech);
}


// --------------------- Flight Search Function ---------------------
const searchButton = document.getElementById('search-button');
const sourceInput = document.getElementById('source-input');
const destinationInput = document.getElementById('destination-input');
const flightResultsContainer = document.getElementById('flight-results');

async function searchFlights() {
    const source = sourceInput.value.trim();
    const destination = destinationInput.value.trim();

    if (!source || !destination) {
        alert("❌ Please enter both source and destination.");
        return;
    }

    flightResultsContainer.innerHTML = "<h2>🔍 Searching for flights...</h2>";

    try {
        // ✅ Corrected Fetch Request (Changed to GET with query parameters)
        const response = await fetch(`http://localhost:5000/flights?source=${source}&destination=${destination}`);

        if (!response.ok) {
            throw new Error(`Server Error: ${response.status}`);
        }

        const data = await response.json();

        if (data.flights && data.flights.length > 0) {
            displayFlightResults(data.flights, source, destination);
        } else {
            flightResultsContainer.innerHTML = "<p>⚠️ No flights found.</p>";
        }        
    } catch (error) {
        console.error("❌ Error fetching flight data:", error);
        flightResultsContainer.innerHTML = "<p>🚨 Something went wrong. Please try again later.</p>";
    }
}


// --------------------- Date & Time Formatting ---------------------
function formatDate(dateString) {
    const dateObj = new Date(dateString);
    if (isNaN(dateObj)) return "N/A";
    return dateObj.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
}

// ✅ Format time string into "03:45 PM"
function formatTime(dateString) {
    const dateObj = new Date(dateString);
    if (isNaN(dateObj)) return "N/A";
    return dateObj.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

// ✅ Function to display flight results in a modern card layout
function displayFlightResults(flights, source, destination) {
    lastSearchedSource = source;
    lastSearchedDestination = destination;
    flightResultsContainer.innerHTML = "";
    filteredFlightsShown = []; // ✅ Reset the list first
    backupFilteredFlights = []; // ✅ Also reset backup



    if (!source || !destination) {
        const warning = document.createElement('p');
        warning.textContent = "⚠️ Please select both source and destination to view available flights.";
        warning.classList.add('no-flights-message');
        flightResultsContainer.appendChild(warning);
        return;
    }

    const resultsHeader = document.createElement('h2');
    resultsHeader.textContent = "✈️ Available Flights";
    resultsHeader.classList.add('results-header');
    flightResultsContainer.appendChild(resultsHeader);

    const flightsGrid = document.createElement('div');
    flightsGrid.classList.add('flights-grid');

    let matchFound = false;

    flights.forEach(flight => {
        if (
            flight.departure.toLowerCase() === source.toLowerCase() &&
            flight.arrival.toLowerCase() === destination.toLowerCase()
        ) {

            console.log("Flight Class:", flight.flight_class); // 👈 Add it here
            
            matchFound = true;


            filteredFlightsShown.push(flight); // ✅ Save this shown flight for Price Alert filtering
            backupFilteredFlights.push(flight); // ✅ Save original shown flights



            // ✅ Fallbacks & formatting
            const airline = flight.airline || "Unknown Airline";
            const arrivalTimeRaw = flight.arrival_time || "N/A";
            const departureTimeRaw = flight.departure_time || "N/A";
            const arrivalTime = formatTime(arrivalTimeRaw);
            const departureTime = formatTime(departureTimeRaw);
            const flightNumber = flight.flight_number || "N/A";
            const seats = flight.seats_available || "N/A";
            const duration = flight.duration || "N/A";
            const departureDate = formatDate(departureTimeRaw);
            const arrivalDate = formatDate(arrivalTimeRaw);

            // ✅ Fix price
            let formattedPrice = !isNaN(flight.price)
                ? parseFloat(flight.price).toLocaleString('en-IN', {
                    style: 'currency',
                    currency: 'INR',
                    minimumFractionDigits: 2
                })
                : "₹N/A";
                
            // ✅ Create flight card
const flightCard = document.createElement('div');
flightCard.classList.add('flight-card');

// ✅ Get dynamic class name from flight_class (e.g., economy, business, first-class)
const classType = flight.flight_class ? flight.flight_class.toLowerCase().replace(/\s+/g, '-') : 'unknown';


flightCard.innerHTML = `
  <div class="flight-header">
    <h3 class="flight-route">🛫 ${flight.departure} → 🛬 ${flight.arrival}</h3>
    <span class="flight-class-tag ${classType}">${flight.flight_class}</span>
  </div>

  <div class="flight-info">
    <p><strong>✈️ Airline:</strong> ${airline}</p>
    <p><strong>🔢 Flight No:</strong> ${flightNumber}</p>
    <p><strong>🛩️ Aircraft:</strong> ${flight.aircraft || "N/A"}</p>

 <div class="flight-times"> 
  <div class="time">
    <p>⏰ <strong>Departure:</strong> ${departureTime}</p>
    <p>📅 <strong>Departure Date:</strong> ${departureDate}</p>
  </div>

      <div class="progress-bar">
        <div class="line"></div>
        <div class="dot start"></div>
        <div class="dot end"></div>
      </div>

      <div class="time">
        <p>🛬 <strong>Arrival:</strong> ${arrivalTime}</p>
        <p>📅 <strong>Arrival Date:</strong> ${arrivalDate}</p>
      </div>
    </div>

    <p><strong>🕒 Duration:</strong> ${duration}</p>
    <p><strong>💺 Seats Available:</strong> ${seats}</p>
    <p><strong>💰 Price:</strong> ${formattedPrice}</p>
  </div>

<a href="/booking" class="book-btn">Book Now</a>
`;

        // ✅ Set dynamic booking link
        const bookBtn = flightCard.querySelector('.book-btn');
        bookBtn.href = `/booking/${flight.id}`; 


flightsGrid.appendChild(flightCard);

        }
    });

    if (!matchFound) {
        const noFlights = document.createElement('p');
        noFlights.textContent = "❌ No flights found for the selected route.";
        noFlights.classList.add('no-flights-message');
        flightResultsContainer.appendChild(noFlights);
    } else {
        flightResultsContainer.appendChild(flightsGrid);
    }
}

// Event listener for search button
searchButton.addEventListener('click', () => {
    selectedSource = sourceInput.value.trim();
    selectedDestination = destinationInput.value.trim();

    if (!selectedSource || !selectedDestination) {
        flightResultsContainer.innerHTML = "";
        const warning = document.createElement('p');
        warning.textContent = "⚠️ Please select both source and destination to view available flights.";
        warning.classList.add('no-flights-message');
        flightResultsContainer.appendChild(warning);
        return; // ✅ STOP here
    }

    // ✅ Inputs are valid, now display flights
    displayFlightResults(flights);
});



// --------------------- Flight Map (Leaflet.js) ---------------------
let flightMap = L.map('flight-map').setView([20.5937, 78.9629], 4); // Default center (India)

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(flightMap);

let flightRoute;

// Define airport locations
const indianAirports = [
    { name: "Sardar Vallabhbhai Patel International", lat: 23.0738, lng: 72.6246 }, // Ahmedabad
    { name: "Chhatrapati Shivaji Maharaj International", lat: 19.0896, lng: 72.8656 }, // Mumbai
    { name: "Indira Gandhi International", lat: 28.5562, lng: 77.1000 }, // Delhi
    { name: "Kempegowda International", lat: 13.1986, lng: 77.7066 }, // Bangalore
    { name: "Rajiv Gandhi International", lat: 17.2403, lng: 78.4294 }, // Hyderabad
    { name: "Jaipur International", lat: 26.8286, lng: 75.8069 }, // Jaipur
    { name: "Chennai International", lat: 12.9941, lng: 80.1707 }, // Chennai
    { name: "Dr. Babasaheb Ambedkar International", lat: 21.0922, lng: 79.0472 }, // Nagpur
];

const internationalAirports = [
    { name: "Hartsfield-Jackson Atlanta Intl", lat: 33.6407, lng: -84.4277 }, // USA
    { name: "Beijing Capital Intl", lat: 40.0799, lng: 116.6031 }, // China
    { name: "Dubai Intl", lat: 25.2532, lng: 55.3657 }, // UAE
    { name: "Los Angeles Intl", lat: 33.9416, lng: -118.4085 }, // USA
    { name: "Tokyo Haneda Intl", lat: 35.5494, lng: 139.7798 }, // Japan
    { name: "London Heathrow Intl", lat: 51.4700, lng: -0.4543 }, // UK
    { name: "Paris Charles de Gaulle Intl", lat: 49.0097, lng: 2.5479 }, // France
    { name: "Frankfurt am Main Intl", lat: 50.0379, lng: 8.5622 }, // Germany
    { name: "Singapore Changi Intl", lat: 1.3644, lng: 103.9915 } // Singapore
];

// Merging both Indian and international airports
const airports = [...indianAirports, ...internationalAirports];




// Function to create a custom marker
function createCustomMarker(className) {
    return L.divIcon({
        className: className,
        iconSize: [30, 30]
    });
}

// Function to add airport markers
function addAirportMarkers() {
    airports.forEach((airport) => {
        L.marker([airport.lat, airport.lng], { icon: createCustomMarker('airport-icon') })
        .addTo(flightMap)
        .bindPopup(`<b>${airport.name} Airport</b>`);
    });
}

// Call function to display airport markers
addAirportMarkers();

// Define 50 airplanes with flight details
const airplanes = [
    { flight: "AI101", lat: 28.5562, lng: 77.1000, from: "Delhi", to: "London" },
    { flight: "BA202", lat: 51.4700, lng: -0.4543, from: "London", to: "New York" },
    { flight: "EK303", lat: 25.2532, lng: 55.3657, from: "Dubai", to: "Singapore" },
    { flight: "SQ408", lat: 1.3644, lng: 103.9915, from: "Singapore", to: "Tokyo" },
    { flight: "LH505", lat: 50.0379, lng: 8.5622, from: "Frankfurt", to: "Mumbai" },
    { flight: "QF105", lat: -33.9399, lng: 151.1753, from: "Sydney", to: "Dubai" },
    { flight: "CX890", lat: 22.3080, lng: 113.9185, from: "Hong Kong", to: "San Francisco" },
    { flight: "AI128", lat: 19.0896, lng: 72.8656, from: "Mumbai", to: "New York" },
    { flight: "AF656", lat: 49.0097, lng: 2.5479, from: "Paris", to: "Delhi" },
    { flight: "VS319", lat: 51.1537, lng: -0.1821, from: "London", to: "New Delhi" },
    { flight: "TK720", lat: 41.2753, lng: 28.7519, from: "Istanbul", to: "Mumbai" },
    { flight: "EY268", lat: 24.4539, lng: 54.3773, from: "Abu Dhabi", to: "Hyderabad" },
    { flight: "BA213", lat: 51.4700, lng: -0.4543, from: "London", to: "Boston" },
    { flight: "QR920", lat: 25.2731, lng: 51.6085, from: "Doha", to: "Auckland" },
    { flight: "SQ421", lat: 12.9941, lng: 80.1707, from: "Chennai", to: "Singapore" },
    { flight: "AI203", lat: 28.5562, lng: 77.1000, from: "Delhi", to: "Sydney" },
    { flight: "DL56", lat: 33.6407, lng: -84.4277, from: "Atlanta", to: "Paris" },
    { flight: "QF9", lat: -37.6690, lng: 144.8410, from: "Melbourne", to: "London" },
    { flight: "LH744", lat: 50.0379, lng: 8.5622, from: "Frankfurt", to: "Singapore" },
    { flight: "NH802", lat: 35.5494, lng: 139.7798, from: "Tokyo", to: "Delhi" }
];

// Function to add airplane markers
function addAirplaneMarkers() {
    airplanes.forEach((airplane) => {
        L.marker([airplane.lat, airplane.lng], { icon: createCustomMarker('airplane-icon') })
        .addTo(flightMap)
        .bindPopup(`<b>Flight ${airplane.flight}</b><br>Route: ${airplane.from} → ${airplane.to}`);
    });
}




// Function to update flight route dynamically
async function updateFlightMap(source, destination) {
    try {
        const response = await fetch(`/api/flight-route?source=${source}&destination=${destination}`);
        const data = await response.json();

        flightMap.setView([data.sourceLat, data.sourceLng], 5);

        if (flightRoute) flightMap.removeLayer(flightRoute);

        // Draw Flight Route Line
        flightRoute = L.polyline([[data.sourceLat, data.sourceLng], [data.destLat, data.destLng]], { color: 'blue' }).addTo(flightMap);

        // Add Departure & Destination Markers
        L.marker([data.sourceLat, data.sourceLng]).addTo(flightMap).bindPopup(`Departure: ${source}`).openPopup();
        L.marker([data.destLat, data.destLng]).addTo(flightMap).bindPopup(`Destination: ${destination}`).openPopup();
    } catch (error) {
        console.error("Error fetching flight route:", error);
    }
}

// Initialize markers after the map loads
flightMap.whenReady(() => {
    addAirportMarkers();
    addAirplaneMarkers();
});


// --------------------- Chatbot Functionality ---------------------
const chatbotBtn = document.getElementById('chatbot-btn');
const chatbot = document.getElementById('chatbot');
const chatbotInput = document.getElementById('chat-input');
const chatbotBody = document.getElementById('chat-body');

chatbotBtn.addEventListener("click", function() {
    chatbot.style.display = chatbot.style.display === "none" || chatbot.style.display === "" ? "block" : "none";
});

async function sendChatMessage(event) {
    if (event.key !== "Enter") return;

    const message = chatbotInput.value.trim();
    if (!message) return;

    const userMessage = document.createElement("p");
    userMessage.classList.add("user-message");
    userMessage.textContent = "You: " + message;
    chatbotBody.appendChild(userMessage);

    chatbotInput.value = "";

    try {
        const response = await fetch(`/api/chatbot?message=${encodeURIComponent(message)}`);
        const data = await response.json();

        const botResponse = document.createElement("p");
        botResponse.classList.add("bot-message");
        botResponse.textContent = "Bot: " + data.response;
        chatbotBody.appendChild(botResponse);
    } catch (error) {
        console.error("Chatbot Error:", error);
        const botResponse = document.createElement("p");
        botResponse.classList.add("bot-message");
        botResponse.textContent = "Bot: Sorry, I'm still learning!";
        chatbotBody.appendChild(botResponse);
    }
}

chatbotInput.addEventListener("keypress", sendChatMessage);

// --------------------- User Reviews ---------------------
const reviewsContainer = document.getElementById('user-reviews');
const stars = document.querySelectorAll('.star');
let selectedRating = 0;

// Handle star rating selection
stars.forEach(star => {
    star.addEventListener('click', function() {
        selectedRating = this.getAttribute('data-value');
        updateStarColors(selectedRating);
    });
});

function updateStarColors(rating) {
    stars.forEach(star => {
        if (star.getAttribute('data-value') <= rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

function submitReview() {
    const reviewText = document.getElementById('review-text').value.trim();
    if (!reviewText || selectedRating === 0) {
        alert("Please provide a review and select a rating.");
        return;
    }

    // Create review element
    const reviewElement = document.createElement('p');
    reviewElement.innerHTML = `<strong>${'⭐'.repeat(selectedRating)}</strong> - ${reviewText}`;
    
    // Append review to the list
    reviewsContainer.appendChild(reviewElement);
    
    // Reset fields
    document.getElementById('review-text').value = "";
    selectedRating = 0;
    updateStarColors(0);
}


// --------------------- Dark Mode Toggle ---------------------
document.addEventListener("DOMContentLoaded", function () {
    const darkModeToggle = document.getElementById("darkModeToggle");
    if (darkModeToggle) {
        darkModeToggle.addEventListener("change", function () {
            document.body.classList.toggle("dark-mode", darkModeToggle.checked);
        });
    }

    // Show Login Form
    window.showLoginForm = function () {
        document.getElementById("login-form").classList.remove("hidden");
        document.getElementById("register-form").classList.add("hidden");
    };

    // Show Register Form
    window.showRegisterForm = function () {
        document.getElementById("register-form").classList.remove("hidden");
        document.getElementById("login-form").classList.add("hidden");
    };

    // Handle Login (Form-Based)
    window.loginUser = function () {
        const formData = new FormData();
        formData.append("email", document.getElementById("login-username").value);
        formData.append("password", document.getElementById("login-password").value);

        fetch("/login", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Login successful!");
                window.location.href = data.redirect || "/";  // Redirect to correct page
            } else {
                alert(data.message || "Invalid login credentials.");
            }
        })        
        .catch(error => console.error("Error:", error));
    };

    // Handle Registration (Form-Based)
    window.registerUser = function () {
        const formData = new FormData();
        formData.append("username", document.getElementById("register-username").value);
        formData.append("email", document.getElementById("register-email").value);
        formData.append("password", document.getElementById("register-password").value);
        formData.append("role", "user"); // Default to 'user'

        fetch("/register", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Registration failed: " + data.error);
            } else {
                alert("Registration successful! Please log in.");
                showLoginForm();
            }
        })
        .catch(error => console.error("Error:", error));
    };
});



// --------------------- Flight Comparison Section ---------------------
document.addEventListener("DOMContentLoaded", function () {
    const comparisonTable = document.querySelector(".comparison-table");
    const searchForm = document.getElementById("searchForm");

    if (comparisonTable) {
        comparisonTable.style.display = "none"; // Hide on page load
    }

    if (searchForm) {
        searchForm.addEventListener("submit", function () {
            if (comparisonTable) {
                setTimeout(() => {
                    comparisonTable.style.display = "block"; // Show after search
                }, 500);
            }
        });
    }
});



// --------------------- Profile Dropdown ---------------------
function toggleProfileDropdown() {
    var dropdown = document.getElementById("profile-dropdown");
    dropdown.classList.toggle("hidden");
}

// Close dropdown when clicking outside
document.addEventListener("click", function (event) {
    var profileBtn = document.getElementById("profile-btn");
    var dropdown = document.getElementById("profile-dropdown");

    if (!profileBtn.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.classList.add("hidden");
    }
});