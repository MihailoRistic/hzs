import sqlite3
import uuid

from model.team import Team
from model.team_member import TeamMember

DB_PATH = "C:\\Users\\DOM\\Desktop\\Projects\\Koncar Crew\\fon hzs\\backend-master\\db\\hzs.db"  # can do abs path too!


def _connect():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    return conn


def get_all_teams():
    conn = _connect()  # todo use connection as context manager
    c = conn.cursor()
    query = """SELECT id, name, description, photo_url, team_uuid FROM team"""
    c.execute(query)
    result_set = c.fetchall()

    teams = []

    for t in result_set:
        created_team = Team(id=t[0], name=t[1], description=t[2], photo_url=t[3], team_uuid=t[4])

        member_query = """SELECT id, first_name, last_name, email, phone_number, school, city FROM 
        team_member WHERE team_id=?"""
        c.execute(member_query, (created_team.id,))
        members = c.fetchall()

        for m in members:
            created_member = TeamMember(id=m[0], first_name=m[1], last_name=m[2], email=m[3], phone_number=m[4],
                                        school=m[5], city=m[6], team=created_team)
            created_team.add_member(created_member)

        teams.append(created_team)

    conn.commit()
    c.close()
    conn.close()

    return teams


def get_team(team_uuid):
    conn = _connect()  # todo use connection as context manager
    c = conn.cursor()
    query = """SELECT id, name, description, photo_url, team_uuid FROM team WHERE team_uuid=?"""
    c.execute(query, (team_uuid,))
    t = c.fetchone()

    if t is None:
        return None

    created_team = Team(id=t[0], name=t[1], description=t[2], photo_url=t[3], team_uuid=t[4])

    member_query = """SELECT id, first_name, last_name, email, phone_number, school, city FROM 
    team_member WHERE team_id=?"""
    c.execute(member_query, (created_team.id,))
    members = c.fetchall()

    for m in members:
        created_member = TeamMember(id=m[0], first_name=m[1], last_name=m[2], email=m[3], phone_number=m[4],
                                    school=m[5], city=m[6], team=created_team)
        created_team.add_member(created_member)

    conn.commit()
    c.close()
    conn.close()

    return created_team


def get_member(team_uuid, member_id):

    conn = _connect()  # todo use connection as context manager
    c = conn.cursor()

    team_uuid = team_uuid[:-1]

    query = """SELECT id, name, description, photo_url, team_uuid FROM team WHERE team_uuid=?"""
    c.execute(query, (team_uuid,))
    t = c.fetchone()

    if t is None:
        return None

    created_team = Team(id=t[0], name=t[1], description=t[2], photo_url=t[3], team_uuid=t[4])

    member_query = """SELECT first_name, last_name, email, phone_number, school, city FROM team_member WHERE
     team_id=? AND id=?"""
    c.execute(member_query, (t[0], member_id))
    m = c.fetchone()
    if m is None:
        return None

    member = TeamMember(id=member_id, first_name=m[0], last_name=m[1], email=m[2], phone_number=m[3], school=m[4],
                        city=m[4], team=created_team)

    conn.commit()
    c.close()
    conn.close()

    return member


def update_member(data):
    conn = _connect()  # todo use connection as context manager
    c = conn.cursor()

    query = """SELECT id FROM team_member WHERE id=? And team_id=?"""
    c.execute(query, (data['id'], data['team_id']))

    if c.fetchone() is None:
        return None

    query = """UPDATE team_member SET first_name=?, last_name=?, email=?, phone_number=?, school=?, city=? WHERE
     team_id=? AND id=?"""

    c.execute(query, (data['first_name'], data['last_name'], data['email'], data['phone_number'], data['school'],
                      data['city'], data['team_id'], data['id']))

    conn.commit()
    c.close()
    conn.close()
    return data


def delete_member(team_uuid, member_id):
    conn = _connect()
    c = conn.cursor()

    team_uuid = team_uuid[:-1]

    query = """SELECT id FROM team WHERE team_uuid=?"""
    c.execute(query, (team_uuid,))
    t = c.fetchone()

    if t is None:
        return None
    try:
        with conn:
            team_query = """DELETE FROM team_member WHERE team_id=? AND id=?"""
            status = conn.execute(team_query, (t[0], member_id))
            success = False
            if status.rowcount == 1:
                success = True

        return success
    except sqlite3.Error:
        return False


def create_team(data):
    conn = _connect()  # todo use connection as context manager
    c = conn.cursor()

    team_query = """INSERT INTO team (name, description, photo_url, team_uuid) VALUES (?,?,?,?)"""
    team_uuid = uuid.uuid4()
    c.execute(team_query, (data['name'], data['description'], data['photo_url'], str(team_uuid)))
    team_id = c.lastrowid
    data['id'] = team_id
    data['team_uuid'] = team_uuid

    for m in data['team_members']:
        member_query = """INSERT INTO team_member (first_name, last_name, email, phone_number, school, city, team_id) 
        VALUES (?,?,?,?,?,?,?)"""
        c.execute(member_query,
                  (m['first_name'], m['last_name'], m['email'], m['phone_number'], m['school'], m['city'], team_id))
        m['id'] = c.lastrowid

    conn.commit()
    c.close()
    conn.close()
    return data


def update_team(data):
    conn = _connect()  # todo use connection as context manager
    c = conn.cursor()

    delete_all_team_members(data['id'])

    team_query = """UPDATE team SET name=?, description=?, photo_url=? WHERE team_uuid=?"""

    c.execute(team_query, (data['name'], data['description'], data['photo_url'], data['team_uuid']))

    for m in data['team_members']:
        member_query = """INSERT INTO team_member (first_name, last_name, email, phone_number, school, city, team_id) 
        VALUES (?,?,?,?,?,?,?)"""
        c.execute(member_query,
                  (m['first_name'], m['last_name'], m['email'], m['phone_number'], m['school'], m['city'], data['id']))
        m['id'] = c.lastrowid

    conn.commit()
    c.close()
    conn.close()
    return data


def delete_team(team_uuid):
    conn = _connect()
    try:
        with conn:
            team_query = """DELETE FROM team WHERE team_uuid=?"""
            status = conn.execute(team_query, (team_uuid,))
            success = False
            if status.rowcount == 1:
                success = True

        return success
    except sqlite3.Error:
        return False


def delete_all_team_members(team_id):
    conn = _connect()
    try:
        with conn:
            team_query = """DELETE FROM team_member WHERE team_id=?"""
            status = conn.execute(team_query, (team_id,))
            success = False
            if status.rowcount > 0:
                success = True

            return success
    except sqlite3.Error:
        return False
