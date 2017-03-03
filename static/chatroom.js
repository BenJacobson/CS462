HTMLCollection.prototype.forEach = Array.prototype.forEach;

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

messageStore = {}
messageNeeds = {}
lastMessageID = originID + ':' + nextMessageID

function scrollToRecentChat() {
	var chatboxes = document.getElementsByClassName("chatbox");
	chatboxes.forEach(function(chatbox) {
		chatbox.scrollTop = chatbox.scrollHeight;
	});
}

function addMessage(message) {
	var li = document.createElement("li");
	var messageNode = document.createTextNode(message);
	li.appendChild(messageNode);
	document.getElementById("messagesList").appendChild(li);
	scrollToRecentChat();
}

function prepareRumor() {
	if (Math.floor(Math.random()*2)) { // Rumor
		lastMessage = messageStore[lastMessageID]
		if (lastMessage)
			return {Rumor: lastMessage};
		else
			return {};
	} else { // Want
		return {Want: messageNeeds};
	}
}

function sendRumor(rumor) {
	var http = new XMLHttpRequest();
	http.open("POST", "/gossip/"+originID, true);
	http.onreadystatechange = function() {
	    if (http.readyState == 4 && http.status == 200 && http.responseText) {
	    	var response = JSON.parse(http.responseText);
	    	if (response.hasOwnProperty('Rumor')) {
	    		// update message needs here
	    		originSeq = response.Rumor.ID.split(':');
	    		if (!messageStore.hasOwnProperty(response.Rumor.ID)) {
	    			messageStore[response.Rumor.ID] = response.Rumor.Message;
	    			addMessage(response.Rumor.Message);
	    		}
	    		origin = originSeq[0];
	    		seq = parseInt(originSeq[1]);
	    		if (messageNeeds.hasOwnProperty(origin)) {
	    			if (messageNeeds[origin] = seq) {
	    				messageNeeds[origin] = seq + 1;
	    			}
	    		} else {
	    			messageNeeds[origin] = seq;
	    		}
	    	}
	    	if (response.hasOwnProperty('Want')) {
	    		
	    	}
	        console.log(response);
	    }
	}
	http.send(JSON.stringify(rumor));
}

function propagate() {
	rumor = prepareRumor();
	sendRumor(rumor);
	setTimeout(propagate, 1000);
}

window.onload = function () {
	document.getElementById("chatMessage")
		.addEventListener("keyup", function(event) {
		if (event.keyCode == 13) {
			document.getElementById("sendMessage").click();
		}
	});
	propagate();
}

function sendChatMessage() {
	textbox = document.getElementById('chatMessage')
	message = textbox.value
	textbox.value = ''

	id = originID + ':' + nextMessageID++
	lastMessageID = id
	messageStore[id] = {ID: id, Message: message}

	addMessage(message)
}
