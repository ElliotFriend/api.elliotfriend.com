from flask import Blueprint

bp = Blueprint('sq', __name__)

from app.sq import side_quest_01
from app.sq import side_quest_02