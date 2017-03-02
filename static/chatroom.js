
function sendChatMessage() {
	textbox = document.getElementById('chatMessage')
	message = textbox.value
	textbox.value = ''

	var li = document.createElement("li");
	var messageNode = document.createTextNode(message);
	li.appendChild(messageNode);
	document.getElementById("messagesList").appendChild(li);
}
