from flask import jsonify, request
from app.fcc import bp

from datetime import datetime

@bp.route('/timestamp', methods=['GET'])
@bp.route('/timestamp/<date>', methods=['GET'])
def show_timestamp(date=None):
    if date == None:
        # figure out the current date and return that
        utc_time = datetime.utcnow()
        epoch = int(datetime.utcnow().timestamp() * 1000)
    else:
        # return the parsed timestamp
        pass
    data = {
        'unix': epoch,
        'utc': utc_time,
    }
    return jsonify(data)
