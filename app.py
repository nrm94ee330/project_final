import os

import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine


from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


#################################################
# Database Setup
#################################################




from config import api_key,mysql_key
from sqlalchemy import create_engine

rds_connection_string = "root:" + mysql_key + "@127.0.0.1/project2_happiness"
engine = create_engine(f'mysql://{rds_connection_string}')

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{rds_connection_string}"
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
#Years_Data = Base.classes.sample_metadata
#Samples = Base.classes.samples

Years_Data = Base.classes.happiness_data
Years = Base.classes.years
Variables = Base.classes.variables

@app.route("/")
def index():
    """Return the homepage."""
    
    return render_template("index.html")


@app.route("/years")
def years():
    """Return a list of sample names."""

    # Use Pandas to perform the sql query
    stmt = db.session.query(Years.year).statement
    df = pd.read_sql_query(stmt,engine)
    df["year"]=df["year"].astype(float)
    return jsonify(df.to_dict(orient="records"))

@app.route("/vars")
def variables():
    """Return a list of sample names."""
    stmt = db.session.query(Variables.vars).statement
    df = pd.read_sql_query(stmt,engine)
    df["vars"]=df["vars"]
    return jsonify(df.to_dict(orient="records"))

@app.route("/years0/<year>")
def year_data(year):
    """Return the MetaData for a given sample.""" 

    sel = [
        Years_Data.Country,
        Years_Data.Happiness_Rank,
        Years_Data.Happiness_Score,
        Years_Data.Economy__GDP_per_Capita_,
        Years_Data.Family,
        Years_Data.Health__Life_Expectancy_,
        Years_Data.Freedom,
        Years_Data.Generosity,
        Years_Data.Trust__Government_Corruption_,
        Years_Data.Dystopia_Residual,    
        Years_Data.year,  
        Years_Data.row_id,   
    ]

    #print(year)
    results = db.session.query(*sel).filter(Years_Data.year == year).all()
    #results = db.session.query(*sel).all()
    # Create a dictionary entry for each row of metadata information
    # f = open("happyController.js", "w")
    # f.write("app.controller(\"ctrl1\",function($scope, $log) { $scope.data = { \n")
    # for result in results:
    #     f.write("'" + str(result[11]) + "' : {" )
    #     f.write("   county : '" + str(result[0]) + "', ")
    #     f.write("   Year : '" + str(result[10]) + "', ")
    #     f.write("   rank : " +  str(result[1]) + ",")
    #     f.write("   happy : " +  str(result[2]) + ",")
    #     f.write("   gdp : " +  str(result[3]) + ",")
    #     f.write("   family : " +  str(result[4]) + ",")
    #     f.write("   health : " +  str(result[5]) + ",")
    #     f.write("   freedom : " +  str(result[6]) + ",")
    #     f.write("   generosity : " +  str(result[7]) + ",")
    #     f.write("   trust : " +  str(result[8]) + ",")
    #     f.write("   pred : " +  str(result[9]) )
    #     f.write("},\n")
         
    # f.write("};});")
    # f.close()

   
    year_data = {}
    for result in results:
        print(result)
        year_data["Country"] = result[0]
        year_data["Happiness_Rank"] = float ( result[1])
        year_data["Happiness_Score"] =float (  result[2])
        year_data["Economy__GDP_per_Capita_"] = float ( result[3])
        year_data["Family"] = float ( result[4])
        year_data["Health__Life_Expectancy_"] = float ( result[5])
        year_data["Freedom"] = float ( result[6])
        year_data["Generosity"] = float ( result[7])
        year_data["Trust__Government_Corruption_"] = float ( result[8])
        year_data["Dystopia_Residual"] = float ( result[9])
        year_data["year"] = float ( result[10])

    # print(year_data)
    
    return jsonify(year_data)
    

@app.route("/years/<sample>")
def samples(sample):
    """Return `otu_ids`, `otu_labels`,and `sample_values`."""
    stmt = db.session.query(Years_Data).filter(Years_Data.year == sample).statement
    df = pd.read_sql_query(stmt, engine)

    #df["year"]=df["year"].astype(float)

    # Filter the data based on the sample number and
    # only keep rows with values above 1
    #sample_data = df.loc[df[sample] > 1, ["Country", "otu_label", sample]]
    sample_data=df.sort_values(by=['Happiness_Rank'])
    #sample_data = df.loc[df[sample] > 1, ["Country", "otu_label", sample]]
    # Format the data to send as json
    data = {
        "Country": sample_data.Country.tolist(),
        "Happiness_Rank": sample_data.Happiness_Rank.values.tolist(),
        "Happiness_Score": sample_data.Happiness_Score.tolist(),
        "Economy__GDP_per_Capita_": sample_data.Economy__GDP_per_Capita_.tolist(),
        "Family": sample_data.Family.tolist(),
        "Health__Life_Expectancy_": sample_data.Health__Life_Expectancy_.tolist(),
        "Freedom": sample_data.Freedom.tolist(),
        "Generosity": sample_data.Generosity.tolist(),
        "Trust__Government_Corruption_": sample_data.Trust__Government_Corruption_.tolist(),
        "Dystopia_Residual": sample_data.Dystopia_Residual.tolist(),
        "year": sample_data.year.tolist(),
    }
    return jsonify(data)


if __name__ == "__main__":
    app.run()
