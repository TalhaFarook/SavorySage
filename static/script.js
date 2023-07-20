const chatbot = document.getElementById('chatbot');
const conversation = document.getElementById('conversation');
const inputForm = document.getElementById('input-form');
const inputField = document.getElementById('input-field');

var latitude = ''
var longitude = ''
var coordCheck

if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
        function(position) {
            
            latitude = position.coords.latitude;
            longitude = position.coords.longitude;

            if (latitude !== undefined && longitude !== undefined) {
                coordCheck = 1;
                console.log(coordCheck)
            }
        },

        function(error) {
            coordCheck = 0;
        }
    );
}
  
inputForm.addEventListener('submit', function(event) {
    
    event.preventDefault();
  
    const input = inputField.value;
    inputField.value = '';
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: "2-digit" });
  
    const message = document.createElement('div');
    message.classList.add('chatbot-message', 'user-message');
    message.innerHTML = `<p class="chatbot-text" style="background-color: lightblue;" sentTime="${currentTime}">${input}</p>`;
    conversation.appendChild(message);
  
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/process_input');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = xhr.responseText;
            const message = document.createElement('div');
            message.classList.add('chatbot-message', 'chatbot');
            message.innerHTML = `<p class="chatbot-text" sentTime="${currentTime}">${response}</p>`;
            conversation.appendChild(message);
            message.scrollIntoView({behavior: "smooth"});
        }
    };
    
    xhr.send(JSON.stringify({ input: input, latitude: latitude, longitude: longitude, coordCheck: coordCheck }));

} );