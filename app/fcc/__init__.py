from flask import Blueprint

bp = Blueprint('fcc', __name__)

from app.fcc import request_header_parser
