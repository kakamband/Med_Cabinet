# app/routes/model_app.py

# Imports
from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from app.models import Cannabis, db, parse_records

# from sklearn.externals import joblib
import joblib
import numpy
import json
import pandas as pd
import pickle

# Register routes
model_routes = Blueprint("model_routes", __name__)

# Load KNN model
nn = joblib.load('./app/data/nn02_model.pkl')

# Load transformer
tf = joblib.load('./app/data/tf_01.pkl')


# Routes
@model_routes.route("/strain_output", methods=['GET', 'POST'])
def model_recommender():

    """creates list with top n recommended strains. <prod>
    Paramaters:
        request: dictionary (json object)
            list of user's strain description
        n: int, optional
            number of recommendations to return, default 5.
    Returns:
        list_model_id: python list of n recommended strains.
    """

    type_list, effect_list, flavor_list = (
        request.form.getlist("type_list"),
        request.form.getlist("effect_list"),
        request.form.getlist("flavor_list")
    )

    # Convert all to lowercase
    type_list = [type_list.lower() for type_list in type_list]
    effect_list = [effect_list.lower() for effect_list in effect_list]
    flavor_list = [flavor_list.lower() for flavor_list in flavor_list]

    # Combine into 1 list
    request_text = [type_list,
                    effect_list,
                    flavor_list
                    ]

    # Merges input lists into 1 string
    result_text = []
    for sublist in request_text:
        for n in sublist:
            result_text.append(n)

    # Joins into a single string
    result_string = [' '.join(str(n) for n in result_text)]

    # Apply transformer to user input string
    output_strain_dense = tf.transform(result_string)

    # Apply model
    _, output_strain_list = nn.kneighbors(output_strain_dense.todense())

    # List of strain ids
    list_strains = []
    for points in output_strain_list:
        for index in points:
            list_strains.append(index)

    # Convert to list
    return_list = [
        str(val)
        for val in list_strains
    ]

    # Return objects from database
    records = Cannabis.query.filter(Cannabis.strain_id.in_(return_list)).all()
    return render_template('results.html', data=records)


# Model route for a text input
@model_routes.route("/output_text", methods=['GET', 'POST'])
def text_model_recommender():

    """creates list with top n recommended strains. <prod>
    Paramaters:
        request: dictionary (json object)
            user's strain description
        n: int, optional
            number of recommendations to return, default 3.
    Returns:
        list_model_id: python list of n recommended strains.
    """

    # Get text input - convert to string
    dict_list = (
        request.form.getlist("dict_list")
    )
    request_text = [dict_list.lower() for dict_list in dict_list]
    result_string = [' '.join(str(n) for n in request_text)]

    # Apply model
    output_strain_dense = tf.transform(result_string)
    _, output_strain_list = nn.kneighbors(output_strain_dense.todense())

    # Create list to query with
    list_strains = []
    for points in output_strain_list:
        for index in points:
            list_strains.append(index)

    return_list = [
        str(val)
        for val in list_strains
    ]

    # Return objects from DB
    records = Cannabis.query.filter(Cannabis.strain_id.in_(return_list)).all()
    return render_template('results.html', data=records)
