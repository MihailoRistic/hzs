from flask import Blueprint, request, jsonify

from controller.main_controller import get_all_teams, create_team, get_team, update_team, delete_team, get_member, update_member, delete_member

teams = Blueprint('teams', __name__, url_prefix='/teams')


@teams.route('/hello', methods=['GET'])
def hello_world():
    return 'Why is this still here? D:'


@teams.route('/', methods=['GET', 'POST'])
def teams_view():
    if request.method == 'GET':  # get all teams
        all_teams = get_all_teams()

        response_body = [t.to_dict() for t in all_teams]
        return jsonify(response_body), 200

    if request.method == 'POST':  # create a new team
        # mention validation issues
        body = request.json
        created = create_team(body)
        return jsonify(created), 201


@teams.route('/<string:team_uuid>', methods=['GET', 'PUT', 'DELETE'])
def single_team_view(team_uuid):
    if request.method == 'GET':  # get the team
        team = get_team(team_uuid)
        if team is None:
            return jsonify({'error': 'team with unique id {} not found'.format(team_uuid)}), 404

        response_body = team.to_dict()
        return jsonify(response_body), 200

    if request.method == 'PUT':  # update the team
        body = request.json
        updated = update_team(body)
        if updated is None:
            return jsonify({'error': 'team with unique id {} not found'.format(team_uuid)}), 404

        return jsonify(updated), 200

    if request.method == 'DELETE':  # remove the team
        success = delete_team(team_uuid)

        if not success:
            return jsonify({'error': 'team with unique id {} not found'.format(team_uuid)}), 404

        return jsonify({}), 204


@teams.route('/<team_uuid>:<int:member_id>', methods=['GET', 'PUT', 'DELETE'])
def single_member_view(team_uuid, member_id):
    print('Uslo u deo za membere')
    if request.method == 'GET':  # get the member
        member = get_member(team_uuid, member_id)
        if member is None:
            return jsonify({'error': 'member with id {} not found'.format(member_id)}), 404

        response_body = member.to_dict()
        return jsonify(response_body), 200

    if request.method == 'PUT':  # update the member
        body = request.json
        updated = update_member(body)
        if updated is None:
            return jsonify({'error': 'member with id {} not found'.format(member_id)}), 404

        return jsonify(updated), 200

    if request.method == 'DELETE':  # remove the member
        success = delete_member(team_uuid, member_id)

        if not success:
            return jsonify({'error': 'member with id {} not found'.format(member_id)}), 404

        return jsonify({}), 204
