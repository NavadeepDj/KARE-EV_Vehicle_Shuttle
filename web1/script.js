// Initialize map and marker
let map, marker;

// Predefined vehicle details
const vehicleDetails = {
    '1': { name: 'John Doe', phone: '+1234567890', distance: 'Calculating...' },
    '2': { name: 'Jane Smith', phone: '+0987654321', distance: 'Calculating...' }
};

// Initialize the Google Map
function initMap() {
    const initialLocation = { lat: 9.55, lng: 77.7 };
    map = new google.maps.Map(document.getElementById('map'), {
        center: initialLocation,
        zoom: 16,
        disableDefaultUI: true, // Removes default UI for a cleaner look
    });

    marker = new google.maps.Marker({
        position: initialLocation,
        map: map,
        title: 'EV Vehicle',
        icon: 'https://maps.google.com/mapfiles/kml/shapes/cabs.png', // Add a custom EV icon
    });

    updateDriverLocation(); // Start tracking the driver's location
}

// Continuously update the driver's location
function updateDriverLocation() {
    setInterval(function () {
        fetch('get_driver_location.php')
            .then(response => {
                // Ensure the response is okay and has content
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Ensure data contains the expected keys
                if (data.latitude && data.longitude) {
                    const latLng = new google.maps.LatLng(data.latitude, data.longitude);
                    marker.setPosition(latLng);
                    map.setCenter(latLng);
                } else {
                    console.error('Invalid data structure:', data);
                }
            })
            .catch(error => {
                console.error('Error fetching driver location:', error);
            });
    }, 5000); // Update every 5 seconds
}


// Calculate distance between pickup and drop locations
function calculateDistance() {
    const directionsService = new google.maps.DirectionsService();
    const pickupLocation = document.getElementById('pickup-location').value;
    const dropLocation = document.getElementById('drop-location').value;

    const request = {
        origin: pickupLocation,
        destination: dropLocation,
        travelMode: 'DRIVING',
    };

    directionsService.route(request, (result, status) => {
        if (status === 'OK') {
            const distance = result.routes[0].legs[0].distance.text;
            const selectedVehicle = document.getElementById('ev-vehicle').value;
            vehicleDetails[selectedVehicle].distance = distance;
            updateVehicleDetails(); // Refresh the vehicle details with the updated distance
        }
    });
}

// Update the vehicle details section dynamically
function updateVehicleDetails() {
    const selectedVehicle = document.getElementById('ev-vehicle').value;
    const details = vehicleDetails[selectedVehicle];
    const vehicleHeading = `EV Vehicle ${selectedVehicle} Details`;

    document.getElementById('vehicle-heading').innerText = vehicleHeading;
    document.getElementById('vehicle-name').innerText = `Name: ${details.name}`;
    document.getElementById('vehicle-phone').innerText = `Phone: ${details.phone}`;
    document.getElementById('vehicle-distance').innerText = `Distance: ${details.distance}`;
}

// Toggle dropdown menu visibility
function toggleMenu() {
    const menu = document.querySelector('.menu');
    menu.classList.toggle('active');
}

// Show QR code modal
function showQR() {
    document.getElementById('qr-section').style.display = 'block';
    new QRCode(document.getElementById('qrcode'), {
        text: "https://your-payment-url.com",
        width: 200,
        height: 200,
        colorDark: "#000000",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.H,
    });
}

// Close QR code modal
function closeQR() {
    document.getElementById('qr-section').style.display = 'none';
    document.getElementById('qrcode').innerHTML = ""; // Clear QR code content
}

// Event Listeners
document.getElementById('ev-vehicle').addEventListener('change', updateVehicleDetails);
document.getElementById('pickup-location').addEventListener('change', calculateDistance);
document.getElementById('drop-location').addEventListener('change', calculateDistance);
window.onload = () => {
    initMap();
    updateVehicleDetails(); // Initialize vehicle details on page load
};
fetch('send_email.php')
    .then(response => {
        console.log('Response headers:', response.headers);
        return response.text(); // Temporarily parse as text to debug response
    })
    .then(text => {
        console.log('Raw response:', text);
        return JSON.parse(text); // Manually parse if valid JSON
    })
    .then(data => console.log('Parsed response:', data))
    .catch(error => console.error('Error:', error));
    
