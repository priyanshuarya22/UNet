from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from . import db
import json

views = Blueprint('views', __name__)

