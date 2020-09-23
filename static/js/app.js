let username = '';
let chatInput = $('#chat-input');
let chatButton = $('#btn-send');
let userList = $('#user-list');
let messageList = $('#messages');



function sendMessage(socket, body) {
    let re = /@\w+/g.exec(body)
    console.log(re);
    if (re){
       console.log(re[0]);
       socket.send(JSON.stringify({
                'command':'message_mentions',
                'username': username,
                'message': body,
                'mentions_user': re[0].slice(1),}));
    }else{
    socket.send(JSON.stringify({
                'command':'message',
                'message': body
            }));
            }
}


function CreateSocket(username) {
    var socket = new WebSocket('ws://' + window.location.host +
        '/ws/'+username+'/')
    return socket
}

function drawMessage(message, p_username) {
    let position = 'left';
    if (p_username === username) position = 'right';
    const messageItem = `
            <li class="message ${position}">
                <div class="avatar">${p_username}</div>
                    <div class="text_wrapper">
                        <div class="text">${message}<br>
                    </div>
                </div>
            </li>`;
    $(messageItem).appendTo('#messages');
}


$(document).ready(function () {
    let socket = ''
    $('.modal').modal('show');
    $('#accept-username').click(function () {
        if ($('#username').val().length >0) {
            username = $('#username').val()
            socket = CreateSocket(username);
            $('.modal').modal('hide');

        } else {
            $('#username').css("border-color", "red").attr("placeholder", 'Type your name please!');
        };

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        if (data.command == 'message') {
            drawMessage(data.message, data.username);
        }else if (data.command == 'leave'){
            console.log(data);
            $('.list-group').empty();
            for (let i = 0; i < data.online.length; i++) {
            const userItem = "<a class='list-group-item user'>"+data.online[i]['username']+"</a>";
            $(userItem).appendTo('.list-group');
            }
            drawMessage('LEAVE channel', data.username);
        }else if (data.command == 'enter'){
            console.log(data);
            $('.list-group').empty();
            for (let i = 0; i < data.online.length; i++) {
                const userItem = "<a class='list-group-item user'>"+data.online[i]['username']+"</a>";
                $(userItem).appendTo('.list-group');
            };
            drawMessage('ENTER channel', data.username);
        }else if (data.command == 'message_mentions'){
            $('#snackbar').html('New message from user '+data.username);
            $('#snackbar').attr('class', 'show');
            setTimeout(function(){$('#snackbar').attr('class', ' '); }, 5000);
            console.log(data);
        }

    };

    });

    chatInput.keypress(function (e) {
        if (e.keyCode == 13)
            chatButton.click();
    });

    chatButton.click(function () {
        if (chatInput.val().length > 0) {
            sendMessage(socket, chatInput.val());
            chatInput.val('');
        }
    });



});



