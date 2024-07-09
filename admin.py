from flask_restful import Resource
from flask import jsonify, request, make_response
from datetime import datetime
from flask_security import roles_accepted, current_user

from database.models import *


class CampaignDelete(Resource):
    @roles_accepted('admin','sponsor')
    def delete(self, id):
        status = Campaign.admin_delete(id)
        if status:
            return make_response(jsonify({"message": "campaign deleted successfully"}), 201)
        return make_response(jsonify({"message": "No campaign found by that id"}), 404)
    
class AdDelete(Resource):
    @roles_accepted('admin','sponsor')
    def delete(self, id):
        # print(id)
        status = Ad.admin_delete(id)
        # status = True
        if status:
            return make_response(jsonify({"message": "Advertisement deleted successfully"}), 201)
        return make_response(jsonify({"message": "No Advertisement found by that id"}), 404)
    
class toggle_user_status(Resource):
    @roles_accepted('admin')
    def put(self, id):
        user = user_datastore.find_user(id=id)
        if not user:
            return make_response(jsonify({"message": "No user found by that id"}), 404)
        user_datastore.toggle_active(user)
        db.session.commit()
        return make_response(jsonify({"message": "user status updated successfully", "email": user.email, "status": user.active}), 201)
    
class UserResources(Resource):
    @roles_accepted('admin')
    def get(self):
        users = User.query.all()
        data = [user.serialize() for user in users]
        if not data:
            return make_response(jsonify({"message": "No user found"}), 404)
        return make_response(jsonify({"message": "get all users", "data": data}), 200)
    
    @roles_accepted('admin')
    def delete(self, id):
        user = user_datastore.find_user(id=id)
        if not user:
            return make_response(jsonify({"message": "No user found by that id"}), 404)
        user_datastore.delete_user(user)
        db.session.commit()
        return make_response(jsonify({"message": "user deleted successfully", "email": user.email}), 200)
    
class InfluencerResources(Resource):
    def get(self):
        influencers = Influencer.query.all()
        data = [influencer.serialize() for influencer in influencers]
        if not data:
            return make_response(jsonify({"message": "No influencer found"}), 404)
        return make_response(jsonify({"message": "get all influencers", "data": data}), 200)
    
class SponsorResources(Resource):
    def get(self):
        sponsors = Sponsor.query.all()
        data = [sponsor.serialize() for sponsor in sponsors]
        if not data:
            return make_response(jsonify({"message": "No sponsor found"}), 404)
        return make_response(jsonify({"message": "get all sponsors", "data": data}), 200)