from flask import jsonify, request
from app.fcc import bp

@bp.route('/whoami', methods=['GET'])
def parse_header():
    print(dir(request.accept_languages))
    data = {
        'ipaddress': request.remote_addr,
        'language': request.accept_languages.to_header(),
        'software': request.user_agent.to_header(),
    }
    return jsonify(data)
