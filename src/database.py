import os, uuid, base64, json
import psycopg2
import config_globals
import datetime
DB_PATH = config_globals.DB_PATH

def add_user(userID):
    conn = None
    curr = None

    try:
        conn = psycopg2.connect(DB_PATH)
        curr = conn.cursor()
        curr.execute(
        "INSERT INTO users (userid, created_on) VALUES (%s, %s)",
        (userID, datetime.datetime.now(),)
        )
        conn.commit()

    except Exception as e:
        raise

    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()

def delete_user(userID):
    """
    Deleting a user from databse on disconnect
    On disconnect:

    Delete users from users
    If in active games, delete the user from that lobby
    If both users are deleted from active games, delete the
    active game lobby
    """
    conn = None
    curr = None
    try:
        conn = psycopg2.connect(DB_PATH)
        curr = conn.cursor()
        curr.execute(
            """
            DELETE FROM users WHERE userid = %s;
            """,
            (userID,)
        )
        conn.commit()

    except Exception as e:
        raise

    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()

def remove_user_from_room(userID, roomID):
    conn = None
    curr = None
    try:
        conn = psycopg2.connect(DB_PATH)
        curr = conn.cursor()
        query = """
            UPDATE active_games SET p1 = NULL
            WHERE p1 = %s AND roomid = %s;

            UPDATE active_games SET p2 = NULL
            WHERE p2 = %s AND roomid = %s;

            DELETE FROM active_games
            WHERE p1 IS NULL and p2 IS NULL and roomid = %s;
            """
        curr.execute(query, (userID, roomID, userID, roomID, roomID,))
        conn.commit()

    except Exception as e:
        raise

    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()

def get_user(userID):
    conn = None
    curr = None
    output = None
    try:
        conn = psycopg2.connect(DB_PATH)
        curr = conn.cursor()
        curr.execute(
        """
        SELECT *
        FROM users
        WHERE userid = %s
        """,
        (userID,)
        )
        output = curr.fetchone()
        if output:
            output = output[0]
    except Exception as e:
        raise

    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()
        return output

def add_room(roomID, p1ID, p2ID=None):
    conn = None
    curr = None

    try:
        conn = psycopg2.connect(DB_PATH)
        curr = conn.cursor()
        curr.execute(
        "INSERT INTO active_games (roomid, p1, p2) VALUES (%s, %s, %s)",
        (roomID, p1ID, p2ID)
        )
        conn.commit()

    except Exception as e:
        raise

    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()

def add_user_to_room(roomID, userID, player="p2"):
    conn = None
    curr = None

    try:
        conn = psycopg2.connect(DB_PATH)
        curr = conn.cursor()

        query = f"""
        UPDATE active_games SET {player} = %s
        WHERE roomid = %s
        """
        curr.execute(query, (userID, roomID,))
        conn.commit()

    except Exception as e:
        raise

    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()

def user_in_room(userID):
    """
    Returns: Room tuple (roomID, p1, p2) if found, null otherwise
    """
    conn = None
    curr = None
    output = None
    try:
        conn = psycopg2.connect(DB_PATH)
        curr = conn.cursor()
        curr.execute(
        """
        SELECT *
        FROM active_games
        WHERE p1 = %s OR p2 = %s
        """,
        (userID,userID,)
        )

        query_result = curr.fetchone()
        if query_result:
            output = query_result

    except Exception as e:
        raise

    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()
        return output

def delete_room(roomID):
    conn = None
    curr = None

    try:
        conn = psycopg2.connect(DB_PATH)
        curr = conn.cursor()
        curr.execute(
        "DELETE FROM active_games WHERE roomid = %s",
        (roomID,)
        )
        conn.commit()

    except Exception as e:
        raise

    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()

def get_room(roomID):
    """
    Returns:
        None if no entry is found
    else tuple: (roomID, p1, p2)
    """
    conn = None
    curr = None
    output = None
    try:
        conn = psycopg2.connect(DB_PATH)
        curr = conn.cursor()
        curr.execute(
        """
        SELECT *
        FROM active_games
        WHERE roomid = %s
        """,
        (roomID,)
        )
        output = curr.fetchone()
    except Exception as e:
        raise

    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()
        return output
