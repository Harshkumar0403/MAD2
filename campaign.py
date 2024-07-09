from flask_restful import Resource
from flask import jsonify, request, make_response
from datetime import datetime
import os 
import random 
from werkzeug.utils import secure_filename
from flask_security import roles_accepted, current_user

from database.models import *


class CampaignResource(Resource):
    @roles_accepted('admin', 'sponsor')
    def post(self):
        data = request.form
        name = data['name']
        sponsor_id = data['sponsor_id']
        if not name:
            return jsonify({"message": "name is required"}), 400
        description = data['description']
        if not description:
            return jsonify({"message": "description is required"}), 400
        start_date_str = data['start_date']
        end_date_str = data['end_date']
        budget = data['budget']
        visibility = data['visibility']
        campaign_img = request.files.get('campaignImg')

        # Debugging: Print out role and token information
        print(f"Current User Roles: {[role.name for role in current_user.roles]}")
        print(f"Authorization Header: {request.headers.get('Authorization')}")

        if campaign_img:
            filename = str(random.randint(100000, 100000000)) + secure_filename(campaign_img.filename)
            image_path = os.path.join(os.path.dirname(__file__), '../frontend/src/assets/campimg', filename)
              # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            campaign_img.save(image_path)
            campaign_img.close()
        else:
            return jsonify({"message": "campaign image is required"}), 400

        goals = data['goals'] 
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({"message": "Invalid date format. Please use YYYY-MM-DD."}), 400
        cate = Campaign(
            name=name,
            sponsor_id=sponsor_id,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            visibility=visibility,
            goals=goals,
            campaign_img=filename
        )
        db.session.add(cate)
        db.session.commit()
        return make_response(jsonify({"message": "category created successfully", "id": cate.id, "name": cate.name}), 201)

    def get(self):
        category = Campaign.query.all()
        data = []
        for categories in category:
            cate = {
                    'id': categories.id,
                    'name': categories.name,
                    'campaign_img': categories.campaign_img,
                    'description': categories.description,
                    'created_at': categories.start_date,
                    'end_date':categories.end_date,
                    'sponsor_id':categories.sponsor_id,
                    'budget':categories.budget,
                    'visibility':categories.visibility,
                    'goals':categories.goals


                }
            data.append(cate)
        print(data)
        if data == []:
            return make_response(jsonify({"message": "No category found"}), 404)
        return make_response(jsonify({"message": "get all categories", "data": data}), 200)
    
class CampaignSpecific(Resource):
    @roles_accepted('admin', 'sponsor', 'influencer')
    def get(self, id):
        campaign = Campaign.query.filter_by(id=id).first()
        if not campaign:
            return make_response(jsonify({"message": "No campaign found"}), 404)
        data = campaign.serialize()
        return make_response(jsonify({"message": "Campaign found", "data": data}), 200)
    
    @roles_accepted('admin', 'sponsor')
    def put(self, id):
        categories = Campaign.query.filter_by(id=id).first()
        if not categories:
            return make_response(jsonify({"message": "No campaign found by that id"}), 404)
        data = request.get_json()
        name = data['name']
        if not name:
            return jsonify({"message": "name is required"})
        description = data['description']
        if not description:
            return jsonify({"message": "description is required"})
        
        categories.name = name
        categories.description = description
        categories.sponsor_id = current_user['id']
        categories.status = data['status']
        categories.start_date = data['start_date']
        categories.end_date = data['end_date']
        categories.budget = data['budget']
        categories.visibility= data['visibility']
        categories.goals = data['goals']
        db.session.commit()
        return jsonify({"message": "update specific category", 'id': id})
    
    def delete(self, id):
        categories = Campaign.query.filter_by(id=id).first()
        if not categories:
            return make_response(jsonify({"message": "No category found by that id"}), 404)
        categories.delete = True
        db.session.commit()
        return jsonify({"message": "delete specific category", 'id': id})
