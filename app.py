from flask import Flask, jsonify, request
from flask_security import verify_password
from flask_restful import Api
from flask_security import Security
from config import LocalDev
from database.models import db, user_datastore
from routes.security import security
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDev)
    db.init_app(app)
    api = Api(app)
    security.init_app(app, user_datastore)
    CORS(app)
    with app.app_context():
        import routes.views

    return app,api

app ,api = create_app()

from routes.auth import  login, register
api.add_resource(login, '/api/login')
api.add_resource(register, '/api/register')

from routes.campaign import CampaignResource, CampaignSpecific
api.add_resource(CampaignResource, '/api/campaign')
api.add_resource(CampaignSpecific, '/api/campaign/<int:id>')

from routes.ad import AdResource, AdSpecific
api.add_resource(AdResource, '/api/Ad')
api.add_resource(AdSpecific, '/api/Ad/<int:id>')

from routes.admin import CampaignDelete,AdDelete, toggle_user_status, UserResources , InfluencerResources,SponsorResources
api.add_resource(CampaignDelete, '/api/category_delete/<int:id>')
api.add_resource(AdDelete, '/api/Ad_delete/<int:id>')
api.add_resource(toggle_user_status, '/api/toggle_user_status/<int:id>')
api.add_resource(UserResources, '/api/users', '/api/user/<int:id>')
api.add_resource(InfluencerResources, '/api/influencers')
api.add_resource(SponsorResources, '/api/sponsors')



if __name__ == '__main__':
    app.run(debug=True)