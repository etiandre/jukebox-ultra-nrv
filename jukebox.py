import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)

import playpause
import search
import admin
import vote
import playlist