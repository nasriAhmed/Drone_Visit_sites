#routes.py
from flask import Flask, request, jsonify
from models import db, init_db, Appraisor, Batch, Content

app = Flask(__name__)

# Initialisation de la base de données
init_db(app)

# Récupérer le profil d'un Appraisor
@app.route('/appraisors/<int:appraisor_id>', methods=['GET'])
def get_appraisor_profile(appraisor_id):
    appraisor = Appraisor.query.get(appraisor_id)
    #tester si appraisor not null
    if appraisor:
        appraisor_data = {
            'nickname': appraisor.nickname,
            'mac': appraisor.mac,
            'last_connection': appraisor.last_connection,
            'installed_firmware': appraisor.installed_firmware,
            'hardware': appraisor.hardware,
            'batch': {
                'name': appraisor.batch.name if appraisor.batch else None,
                'firmware': appraisor.batch.firmware if appraisor.batch else None,
                'compatible_hardware': appraisor.batch.compatible_hardware if appraisor.batch else None,
            },
            'contents': [{'name': content.name, 'url': content.url} for content in appraisor.contents]
        }
        return jsonify(appraisor_data)
    return jsonify({'message': 'Appraisor not found'}), 

#Indiquer l'installation d'une version de firmware par un Appraisor
@app.route('/appraisors/<int:appraisor_id>/install-firmware', methods=['POST'])
def install_firmware(appraisor_id):
    appraisor = Appraisor.query.get(appraisor_id)
    if appraisor:
        data = request.get_json()
        version = data.get('version')
        appraisor.install_firmware(version)
        db.session.commit()
        return jsonify({'message': f'Firmware version {version} installed by Appraisor {appraisor_id}'}), 200
    return jsonify({'message': 'Appraisor not found'}), 404
#Initier la mise à jour du firmware d'un batch par un opérateur externe
@app.route('/batches/<int:batch_id>/update-firmware', methods=['POST'])
def update_firmware(batch_id):
    batch = Batch.query.get(batch_id)
    if batch:
        data = request.get_json()
        new_firmware_version = data.get('new_firmware_version')
        batch.initiate_firmware_update(new_firmware_version)
        db.session.commit()
        return jsonify({'message': f'Firmware update initiated for Batch {batch_id}'}), 200
    return jsonify({'message': 'Batch not found'}), 404

#ajouter un nouveau content mandatory
@app.route('/contents/add-mandatory-content', methods=['POST'])
def add_mandatory_content():
    try:
        data = request.get_json()
        content_name = data.get('name')
        url = data.get('url')
        mandatory = data.get('mandatory')
        min_version = data.get('min_version')
        max_version = data.get('max_version')
        firmware_id = data.get('firmware_id')  # Added firmware_id

        # Validate required fields
        if not all([content_name, mandatory, min_version, max_version]):
            return jsonify({'error': 'Missing required data in JSON'}), 400

        # Convert 'mandatory' to a boolean
        mandatory = bool(mandatory)

        # Create Content object and associate it with a specific firmware
        content = Content(
            name=content_name,
            url=url,
            mandatory=mandatory,
            min_version=min_version,
            max_version=max_version,
            firmware_id=firmware_id  # Assuming Content has a relationship with Firmware
        )

        db.session.add(content)
        db.session.commit()

        return jsonify({'message': 'Mandatory content added successfully'}), 201  # 201 Created
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # 500 Internal Server Error



#Ajouter ou retirer un contenu non obligatoire pour un Appraisor
@app.route('/appraisors/<int:appraisor_id>/manage-content', methods=['POST'])
def manage_appraisor_content(appraisor_id):
    appraisor = Appraisor.query.get(appraisor_id)
    if appraisor:
        data = request.get_json()
        content_name = data.get('name')
        content_url = data.get('url')
        action = data.get('action')  # 'add' ou 'remove'

        content = Content.query.filter_by(name=content_name, url=content_url).first()
        print('content', content)
        if content:
            if action == 'add':
                appraisor.add_additional_content(content)
                db.session.commit()
                return jsonify({'message': f'Non-mandatory content added to Appraisor {appraisor_id}'}), 200
            elif action == 'remove':
                appraisor.remove_additional_content(content)
                db.session.commit()
                return jsonify({'message': f'Non-mandatory content removed from Appraisor {appraisor_id}'}), 200
            else:
                return jsonify({'message': 'Invalid action. Use "add" or "remove"'}), 400
        return jsonify({'message': 'Content not found'}), 404
    return jsonify({'message': 'Appraisor not found'}), 404

#main
if __name__ == "__main__":
    app.run(debug=True)