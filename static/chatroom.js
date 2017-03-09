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

var originID = guid()
var nextMessageID = 0
var myEndpoint = 'https://' + window.location.hostname + '/gossip/' + originID
var myName = 'Anon';

var otherEndpoints = []
var messageStore = {}
var messageNeeds = {}
var lastMessageID = originID + ':' + nextMessageID

function getGossipEndpoints() {
	var http = new XMLHttpRequest();
	http.open("GET", "/gossip/endpoints", true);
	http.onreadystatechange = function() {
	    if (http.readyState == 4 && http.status == 200) {
	    	var response = JSON.parse(http.responseText);
	    	otherEndpoints = response;
	    }
	}
	http.send();
}

function addNewEndpoint(newEndpoint) {
	if (!otherEndpoints.includes(newEndpoint)) {
		otherEndpoints.push(newEndpoint);
	}
}

function userAddNewEndpoint() {
	var newEndpointElement = document.getElementById('newEndpoint');
	var newEndpoint = newEndpointElement.value;
	addNewEndpoint(newEndpoint);
	newEndpointElement.value = '';
}

function scrollToRecentChatMessage() {
	var chatboxes = document.getElementsByClassName("chatbox");
	chatboxes.forEach(function(chatbox) {
		chatbox.scrollTop = chatbox.scrollHeight;
	});
}

function addChatMessage(name, message) {
	if (name == undefined) name = 'Anon';
	var li = document.createElement("li");
	var messageNode = document.createTextNode(name + ': ' + message);
	li.appendChild(messageNode);
	document.getElementById("messagesList").appendChild(li);
	scrollToRecentChatMessage();
}

function randomChoice(choices) {
	var index = Math.floor(Math.random() * choices.length);
	return choices[index];
}

function prepareGossipMessage() {
	if (Math.floor(Math.random()*2)) { // Rumor
		lastMessage = messageStore[lastMessageID]
		if (lastMessage)
			return {Rumor: lastMessage, EndPoint: myEndpoint};
	} else { // Want
		wants = [];
		for (key in messageNeeds) {
			wants.push(key + ':' + messageNeeds[key]);
		}
		return {Want: wants, EndPoint: myEndpoint};
	}
	return {};
}

function sendGossipMessage(gossipMessage, otherEndpoint) {
	var http = new XMLHttpRequest();
	http.open("POST", otherEndpoint, true);
	http.send(JSON.stringify(gossipMessage));
}

function propagateGossipMessage() {
	var otherEndpoint = randomChoice(otherEndpoints);
	if (otherEndpoint != undefined) {
		gossipMessage = prepareGossipMessage();
		sendGossipMessage(gossipMessage, otherEndpoint);
	}
	setTimeout(propagateGossipMessage, 1000);
}

function receiveGossipMessage(gossipMessage) {
	addNewEndpoint(gossipMessage.EndPoint);
	if (gossipMessage.hasOwnProperty('Rumor')) {
		// update message needs here
		var originSeq = gossipMessage.Rumor.MessageID.split(':');
		if (!messageStore.hasOwnProperty(gossipMessage.Rumor.MessageID)) {
			messageStore[gossipMessage.Rumor.MessageID] = gossipMessage.Rumor;
			addChatMessage(gossipMessage.Rumor.Originator, gossipMessage.Rumor.Text);
		}
		origin = originSeq[0];
		seq = parseInt(originSeq[1]);
		if (messageNeeds.hasOwnProperty(origin)) {
			if (messageNeeds[origin] == seq) {
				messageNeeds[origin] = seq + 1;
			}
		} else {
			messageNeeds[origin] = seq;
		}
	}
	if (gossipMessage.hasOwnProperty('Want')) {
		gossipMessage.Want.forEach(function (messageID) {
			if (messageStore.hasOwnProperty(messageID)) {
				// prepare gossipMessage rumor and end it
				rumor = {};
				rumor.Rumor = messageStore[messageID];
				rumor.EndPoint = myEndpoint
				sendGossipMessage(rumor, gossipMessage.EndPoint);
			}
		});
	}
}

function retrieveGossipMessage() {
	var http = new XMLHttpRequest();
	http.onreadystatechange = function() {
	    if (http.readyState == 4 && http.status == 200 && http.responseText) {
	    	var response = JSON.parse(http.responseText);
	    	receiveGossipMessage(response);
	    }
	}
	http.open('GET', '/retrieve/'+originID, true);
	http.send();
	setTimeout(retrieveGossipMessage, 1000);
}

function sendChatMessage() {
	textbox = document.getElementById('chatMessage')
	message = textbox.value
	textbox.value = ''

	id = originID + ':' + nextMessageID++
	lastMessageID = id
	messageStore[id] = {MessageID: id, Originator: myName, Text: message}

	addChatMessage(myName, message)
}

window.onload = function () {
	document.getElementById('endpoint').innerHTML += originID;
	document.getElementById("chatMessage")
		.addEventListener("keyup", function(event) {
		if (event.keyCode == 13) {
			document.getElementById("sendMessage").click();
		}
	});
	var chatNameElement = document.getElementById("chatName");
	chatNameElement.addEventListener("keyup", function(event) {
		myName = chatNameElement.value;
	});
	myName = chatNameElement.value;
	getGossipEndpoints();
	propagateGossipMessage();
	retrieveGossipMessage();
}
