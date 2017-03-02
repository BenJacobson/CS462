
function s4() {
  return Math.floor((1 + Math.random()) * 0x10000)
    .toString(16)
    .substring(1);
}

function guid() {
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}

originID = guid()
nextMessageID = 0

messageStore = []
var socket = null

window.onload = function () {
	document.getElementById("chatMessage")
		.addEventListener("keyup", function(event) {
		if (event.keyCode == 13) {
			document.getElementById("sendMessage").click();
		}
	});
	var url = "http://" + document.domain + ":" + location.port;
	// var socket = io.connect(url + "/dd");
	socket = new WebSocket("ws://ec2-52-25-168-24.us-west-2.compute.amazonaws.com/dd")
}

function sendChatMessage() {
	textbox = document.getElementById('chatMessage')
	message = textbox.value
	textbox.value = ''

	var li = document.createElement("li");
	var messageNode = document.createTextNode(message);
	li.appendChild(messageNode);
	document.getElementById("messagesList").appendChild(li);

	id = originID + ':' + nextMessageID++
	console.log(id)
	socket.send(id)
}
