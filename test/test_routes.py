# tests/test_routes.py
import json
import pytest
from flask import Flask
from app.models import Appraisor, Batch, Firmware, Content, db, init_db
#from datetime import datetime

app = Flask(__name__)
init_db(app)

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            yield client
            db.session.rollback()
            #db.drop_all()

def create_sample_data():
    # Creation d'une data pour le test
    with app.app_context():
        batch = Batch(name='TestBatch', firmware='TestFirmware', compatible_hardware=['hardware1'])
        firmware = Firmware(version='1.0.0', url='https://firmware.com', compatible_hardware=['hardware1'])
        content = Content(name='TestContent', url='https://content.com', mandatory=True)
        appraisor = Appraisor(nickname='TestDrone', mac='AA:BB:CC:DD:EE:FF', last_connection='2023-01-01', installed_firmware='1.0.0', hardware='hardware1', batch=batch)
        appraisor.contents.append(content)
        
        try:
            db.session.add_all([batch, firmware, content, appraisor])
            db.session.commit()
        except Exception as e:
            print("Error during database insertion:", e)
            db.session.rollback()
        
     
def test_get_appraisor_profile(client):
    #tester la Récupéreration du profil d'un Appraisor
    create_sample_data()
    print(Appraisor.query.all())
    
    response = client.get(f'/appraisors/1')
    print('response', response, flush=True)
    print('response content', response.data)
    try:
        data = response.get_json()
        assert response.status_code == 200
        assert data['nickname'] == 'TestDrone'
        assert data['batch']['name'] == 'TestBatch'
        assert data['contents'][0]['name'] == 'TestContent'
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)

def test_install_firmware(client):
    create_sample_data()

    response = client.post('/appraisors/1/install-firmware', json={'version': '2.0'})
    assert response.status_code == 200

    appraisor = Appraisor.query.get(1)
    assert appraisor.installed_firmware == '2.0'

def test_update_firmware(client):
    create_sample_data()

    response = client.post('/batches/1/update-firmware', json={'new_firmware_version': '2.1'})
    assert response.status_code == 200

    batch = Batch.query.get(1)
    assert batch.firmware == '2.1'

def test_add_mandatory_content(client):
    response = client.post('/contents/add-mandatory-content', json={
        'name': 'NewMandatoryContent',
        'url': 'http://example.com/new-mandatory-content',
        'mandatory': True,
        'min_version': '1.0',
        'max_version': '2.0',
        'firmware_id': 1
    })

    assert response.status_code == 201

    content = Content.query.filter_by(name='NewMandatoryContent').first()
    assert content is not None

def test_manage_appraisor_content_add(client):
    create_sample_data()

    response = client.post('/appraisors/1/manage-content', json={
        'name': 'AdditionalContent',
        'url': 'http://example.com/additional-content',
        'action': 'add'
    })

    assert response.status_code == 200

    appraisor = Appraisor.query.get(1)
    assert len(appraisor.contents) == 2  

def test_manage_appraisor_content_remove(client):
    create_sample_data()

    response = client.post('/appraisors/1/manage-content', json={
        'name': 'TestContent',
        'url': 'http://example.com/test',
        'action': 'remove'
    })

    assert response.status_code == 200

    appraisor = Appraisor.query.get(1)
    assert len(appraisor.contents) == 0