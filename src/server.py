from flask import Flask, request, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_cors import CORS, cross_origin
from src import database
import uuid, base64, json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
socketio = SocketIO(app, cors_allowed_origins="*")

"""
Current status of lobby and gamestate:
status:
    "dne": If the lobby attempting to join does not exist
    "full": If the lobby attempting to join is full
    "active": If the lobby is active with 2 players tracking state
    "waiting": If the lobby is waiting for players
    "disconnected": If a player in the lobby disconnected

roomID: roomID
p1ID: p1ID
p2ID: p2ID
"""
def lobby_status(status, roomID, p1ID, p2ID):
    obj = {
        "status": status,
        "roomID": roomID,
        "p1ID": p1ID,
        "p2ID": p2ID,
    }
    return obj

@socketio.on('connect')
def connect():
    sid = request.sid
    database.add_user(sid)
    emit("connection_accepted", sid)

@socketio.on('disconnect')
def disconnect():
    """
    Clean up database on disconnect, destroy active_game lobbies
    if disconnecting player is the last player in the lobby

    Emits "disconnect" status to prompt other player in lobby to
    also disconnect from the socket
    """
    sid = request.sid
    room_data = database.user_in_room(sid)
    if room_data:
        payload = lobby_status("disconnected",room_data[0],None,None)
        database.remove_user_from_room(sid, room_data[0])
        emit('lobby_status', payload, room=room_data[0], broadcast=True)
        leave_room(room_data[0])

    database.delete_user(sid)

@socketio.on('create_lobby')
def create_lobby():
    """
    Returns:
        lobby_status object
    """
    sid = request.sid
    room_data = database.user_in_room(sid)
    if not room_data:
        roomID = base64.urlsafe_b64encode(uuid.uuid1().bytes).rstrip(b'=').decode('ascii')[:6]
        database.add_room(roomID, sid)
        join_room(roomID)
        payload = lobby_status("waiting", roomID, sid, None)
        emit("lobby_status", payload, room=roomID)

@socketio.on('join_lobby')
def join_lobby(data):
    """
    Args:
        data (json): {"roomID": ID of room}

    Returns:
        Emits a lobby_status depending on the room state
    """
    sid2 = request.sid
    roomID = data['roomID']
    room_data = database.get_room(roomID)
    if room_data:
        roomID, p1, p2 = room_data
        # lobby is full
        if p1 and p2:
            payload = lobby_status("full", roomID, None, None)
            emit("lobby_status", payload)

        # lobby needs player 2
        if not p2 and p1:
            database.add_user_to_room(roomID, sid2)
            join_room(roomID)
            payload = lobby_status("active", roomID, p1, sid2)
            emit("lobby_status", payload, room=roomID, broadcast=True)

    else:
        # lobby does not exist
        payload = lobby_status("dne", roomID, None, None)
        emit("lobby_status", payload)

@socketio.on('make_move')
def make_move(data):
    """
    Args:
        data (json):
        {
            "roomID": roomid
            "move": [] coords
            "sender": "p1" or "p2"
        }

    Returns:
        Emits on socket 'get_move' the move and sender
    """
    emit('get_move', data, room=data['roomID'])

if __name__ == "__main__":
    socketio.run(app)
