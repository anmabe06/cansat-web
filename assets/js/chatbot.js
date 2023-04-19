const chat = document.getElementById("chatbot-chat");
const timeFlightInit = new Date('2023-04-17 08:22:59+0000');


$("#chatbot-open-container").click(function(){
    $("#open-chat-button").toggle(200);
    $("#close-chat-button").toggle(200);
    $("#chatbot-container").fadeToggle(200);
});

document.getElementById("chatbot-new-message-send-button").addEventListener("click", newInput);

document.getElementById("chatbot-input").addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        newInput();
    }
});

function newInput(){
    newText = document.getElementById("chatbot-input").value;
    if (newText != ""){
        document.getElementById("chatbot-input").value = "";
        addMessage("sent", newText);
        generateResponse(newText);
    }
}


function addMessage(type, text){
    let messageDiv = document.createElement("div");
    let responseText = document.createElement("p");
    responseText.innerHTML = text;
    
    if (type == "sent"){
        messageDiv.classList.add("chatbot-messages", "chatbot-sent-messages");
    } else if (type == "received"){
        messageDiv.classList.add("chatbot-messages", "chatbot-received-messages");
    }

    messageDiv.appendChild(responseText);
    chat.prepend(messageDiv);
}

function addSeconds(date, seconds) {
    let newDateSeconds = date.setSeconds(date.getSeconds() + parseInt(seconds));
    let newDateTemp = new Date(newDateSeconds);
    newDateTemp = new Date(newDateTemp.toUTCString());
    newDateTemp = newDateTemp.toISOString().split(".")[0];
    newDateTemp = newDateTemp.split("T");
    let newDate = newDateTemp[0] + " " + newDateTemp[1];

    return newDate;
}

function generateResponse(prompt){
    if(prompt == "--format"){
        addMessage("received", "The format for the messages sent should be: <b><pre>parameter, second_of_flight</pre></b>Notice the comma, followed by the space.");
    }else if(prompt == "--params"){
        addMessage("received", "The list of available params are: <ul><li>latitude</li><li>longitude</li><li>altitude</li><li>course</li><li>net_velocity</li><li>vertical_acceleration</li><li>vertical_speed</li><li>x_rotation</li><li>y_rotation</li><li>internal_temperature_1</li><li>internal_temperature_2</li><li>external_temperature</li><li>iaq</li><li>pressure</li><li>humidity</li><li>bvoc</li><li>co2</li><li>uva_1</li><li>uva_2</li><li>beta_particles</li><li>satellites_connected</li></ul>");
    }else{
        try{
            prompts = prompt.split(", ");

            let param = prompts[0];
            let seconds = prompts[1];
            let datetime = addSeconds(new Date('2023-04-17 08:22:59+0000'), seconds);

            // Here you can add your answer-generating code
            jQuery.ajax({
                type: "POST",
                url: 'get_value_api.php?param=' + param + '&time=' + datetime,
                dataType: 'json',
                data: {functionname: 'add', arguments: [1, 2]},

                success: function (obj, textstatus) {
                    if(textstatus == 'success'){
                        if(obj.hasOwnProperty("error")){
                            addMessage("received", obj["error"]);
                        }else{
                            addMessage("received", "<b>" + seconds + " seconds</b> after launch, HPS detected <b>" + param + "</b> to be: <b>" + obj[param] + "</b>");
                        }
                    }
                }
            });
        } catch(error) {
            addMessage("received", "Ooop, I don't think I understand you...");
            console.error(error);
        }
    }
}