from flask_restful import Resource
from flask import jsonify, request, make_response
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_security import roles_accepted, current_user
import random
import os 


from database.models import *

class AdResource(Resource):
    @roles_accepted('admin', 'sponsor')
    def post(self):
        data = request.form
        name = data['name']
        if not name:
            return jsonify({"message": "name is required"})
        
        content = data['content']
        campaign_id = data['campaign_id']
        sponsor_id = data['sponsor_id']
        start_date = data['start_date']
        requirements = data['requirements']
        budget = data['budget']
        target_audience = data['target_audience']
        status = data.get('status').lower() == 'true'
        img = request.files['ad_img']

        if img:
            filename = str(random.randint(100000, 100000000)) + secure_filename(img.filename)
            image_path = os.path.join(os.path.dirname(__file__), '../frontend/src/assets/campimg', filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            img.save(image_path)
            img.close()
        else :
            img=""
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"message": "Invalid date format. Please use YYYY-MM-DD."}), 400
        ad = Ad(name=name,content=content, campaign_id=campaign_id, sponsor_id=sponsor_id,
                start_date=start_date, requirements=requirements, budget=budget, 
                target_audience=target_audience, status=status, img=filename)
        
        db.session.add(ad)
        db.session.commit()
        
        return make_response(jsonify({"message": "ad created successfully", "id": ad.id, "name": ad.ad_name}), 201)

    @roles_accepted('admin', 'sponsor', 'influencer')
    def get(self):
        ads = Ad.query.all()
        data = [ad.serialize() for ad in ads]
        if not data:
            return make_response(jsonify({"message": "No advertisements found"}), 404)
        return make_response(jsonify({"message": "get all advertisements", "data": data}), 200)


class AdSpecific(Resource):
    @roles_accepted('admin', 'sponsor', 'influencer')
    def get(self, id):
        ad = Ad.query.filter_by(id=id).first()
        if not ad:
            return make_response(jsonify({"message": "No Advertisment found by that id"}), 404)
        ad = ad.serialize()
        return jsonify({"message": "get specific advertisment", "data": ad})
    
    @roles_accepted('admin', 'manager')
    def put(self, id):
        ad = Ad.query.filter_by(id=id).first()
        if not ad:
            return make_response(jsonify({"message": "No Advertisment found by that id"}), 404)
        data = request.get_json()
        name = data.get('ad_name')
        if not name:
            return jsonify({"message": "name is required"})
        ad_content = data.get('ad_content')
        if not ad_content:
            return jsonify({"message": "ad_content is required"})
        budget = data.get('budget')
        if budget is None:  # Assuming price can be 0, which is falsy
            return jsonify({"message": "budget is required"})
        requirements = data.get('requirements')
        if budget is None:  # Assuming price can be 0, which is falsy
            return jsonify({"message": "requirements is required"})
        ad.ad_name = name
        ad.ad_content = ad_content
        ad.budget=budget
        ad.updated_at = datetime.now()
        ad.requirements = requirements
        # if current_user.has_role('admin'):
        #     product.status = True
        # else:
        #     product.status = False
        db.session.commit()
        return jsonify({"message": "update specific ad", 'id': id})
    
    @roles_accepted('admin', 'manager')
    def delete(self, id):
        ad = Ad.query.filter_by(id=id).first()
        if not ad:
            return make_response(jsonify({"message": "No ad found by that id"}), 404)
        ad.delete = True  # Assuming there's a 'delete' attribute; might need adjustment
        db.session.commit()
        return jsonify({"message": "delete specific ad", 'id': id})
    
    @roles_accepted('admin', 'manager')
    def patch(self, id):
        ad = Ad.query.filter_by(id=id).first()
        if not ad:
            return make_response(jsonify({"message": "No ad  found by that id"}), 404)
        ad.status = not ad.status
        db.session.commit()
        if ad.status:
            return jsonify({"message": "Advertisement activated", 'id': id})
        return jsonify({"message": "Advertisement deactivated", 'id': id})
    
