import os
import json
import random
from flask import render_template, jsonify, send_from_directory
from resources import app, api, mongo
from Junk import Junk, JunkList

from lib.dna import get_random_dna
from lib.generator import ObjectGenerator, MarkovGenerator
from lib.corpus import *
from lib.nlp import NLP

# init patents db
patents=PatentCorpus('../../junkware-data/patents/Patents.sqlite3')

# routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/junks')
def junk_index():
    junks= [x for x in mongo.db.junks.find()]
    return render_template('index.html', junks=junks)

@app.route('/junk/new')
def junk_new():
    return render_template('junk/create.html')

@app.route('/junk/partials/<path:path>')
def partials(path):
    print path
    return render_template(os.path.join('partials',path+".html"))

@app.route('/junk/<ObjectId:objectId>')
def junwkare(objectId):
    junk=mongo.db.junks.find_one_or_404({"_id": objectId})
    print junk
    return render_template('junk/view.html', objectId=objectId, junk=junk)

@app.route('/junk/<ObjectId:objectId>/<path:path>')
def single_junk(objectId, path):
    junk=mongo.db.junks.find_one_or_404({"_id": objectId})
    return render_template(os.path.join('partials',path+".html"), objectId=objectId, junk=junk)

# data
@app.route('/data/randomDNA')
def get_dna():
    my_dna=get_random_dna()
    return jsonify({"dna":my_dna})

@app.route('/data/randomMolecule')
def get_molecules_list():
    files=os.listdir("../../junkware-data/molecules")
    molecules=[mol for mol in files if mol[-4:][:3]=="pdb"]
    print molecules
    return jsonify({"molecules":molecules})

@app.route('/data/molecules/<path:path>')
def get_molecule_file(path):
    app_path =os.path.dirname(os.path.abspath(os.getcwd()))
    data_path= os.path.join(os.path.dirname(app_path), 'junkware-data')
    molecule_path=os.path.join(data_path, "molecules")
    return send_from_directory(molecule_path, path)

# API
api.add_resource(JunkList, '/api/junks')
api.add_resource(Junk, '/api/junk/<ObjectId:junk_id>')

@app.route('/api/junk/<ObjectId:objectId>/dna')
def get_junk_dna(objectId):
    junk=mongo.db.junks.find_one_or_404({"_id": objectId})
    return jsonify({"dna":junk["dna"]})

@app.route('/api/junk/<ObjectId:objectId>/molecule')
def get_junk_molecule(objectId):
    junk=mongo.db.junks.find_one_or_404({"_id": objectId})
    return jsonify({"molecule":junk["molecule"]})

@app.route('/api/junk/<ObjectId:objectId>/title')
def get_junk_title(objectId):
    junk=mongo.db.junks.find_one_or_404({"_id": objectId})
    pats=patents.get_records_by_ids(junk["patents_ids"])

    # title
    titles=""
    for t in pats[1]:
        titles += " "+t
    title= MarkovGenerator(titles).generate_text(size=random.randint(4,7)).title()

    return jsonify({ "title" : title })

@app.route('/api/junk/<ObjectId:objectId>/abstract')
def get_junk_abstract(objectId):
    junk=mongo.db.junks.find_one_or_404({"_id": objectId})
    pats=patents.get_records_by_ids(junk["patents_ids"])

    # abstract
    abstract_corpus_path = os.path.join(os.path.dirname(os.getcwd()), 'corpus_abstract')
    abstract_generator = ObjectGenerator(abstract_corpus_path)

    # add patents to corpus
    for abstract in pats[0]:
        clean_abstract=NLP(abstract).filter_out_nastyness()
        abstract_generator.add_to_corpus(clean_abstract)
        # print type(clean_abstract)

    # create abstract
    abstract_generator.load_corpus()
    abstract = abstract_generator.generate_definition(1,10)
    print abstract

    return jsonify({ "abstract" : abstract })

@app.route('/api/junk/<ObjectId:objectId>/description')
def get_junk_description(objectId):
    junk=mongo.db.junks.find_one_or_404({"_id": objectId})
    pats=patents.get_records_by_ids(junk["patents_ids"])

    # abstract
    abstract_corpus_path = os.path.join(os.path.dirname(os.getcwd()), 'corpus_abstract')
    abstract_generator = ObjectGenerator(abstract_corpus_path)

    # add patents to corpus
    for abstract in pats[0]:
        clean_abstract=NLP(abstract).filter_out_nastyness()
        abstract_generator.add_to_corpus(clean_abstract)

    # description
    description = []
    for i  in range(0,random.randint(10,25)):
        description.append(abstract_generator.generate_definition(1,random.randint(30,150)))

    return jsonify({ "description" : description })


# STATIC
@app.route('/js/<path:path>')
def js_static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('js', path))

@app.route('/css/<path:path>')
def css_static_proxy(path):
    print os.path.join('css', path)
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('css', path))

@app.route('/lib/<path:path>')
def lib_static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('lib', path))

@app.route('/libs/<path:path>')
def libs_static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('libs', path))

@app.route('/img/<path:path>')
def img_static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('img', path))

@app.route('/data/<path:path>')
def data_static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('data', path))
