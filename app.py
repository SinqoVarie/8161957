from flask import Flask, jsonify
import requests

app = Flask(__name__)

# إعدادات المتغيرات
PLAYER_ID_PATH = '/like/<player_id>'
API_URL = 'https://likes.freefireinfo.site/api/sg/{}?key=kazwi'
SUCCESS_MESSAGE_TEMPLATE = '''
- Done Send Likes ✅
–––––––––––––––––
- Player Name : {player_name}
- Player Id : {player_id}
- Likes Before : {likes_before}
- Likes After : {likes_after}
- Likes Given : {likes_given}
–––––––––––––––––
- Dev : C4 - Team 
- Tg : @C4_Team_Officiel
'''

# دالة للحصول على معلومات اللاعب من API
def fetch_player_info(player_id):
    response = requests.get(API_URL.format(player_id))
    if response.status_code == 200:
        return response.json()['response']
    return None

# دالة لمعالجة أوامر الإعجاب
@app.route(PLAYER_ID_PATH, methods=['GET'])
def handle_like_command(player_id):
    player_info = fetch_player_info(player_id)

    if player_info:
        # تنسيق الرسالة
        message = SUCCESS_MESSAGE_TEMPLATE.format(
            player_name=player_info["PlayerNickname"],
            player_id=player_info["UID"],
            likes_before=player_info["LikesbeforeCommand"],
            likes_after=player_info["LikesafterCommand"],
            likes_given=player_info["LikesGivenByAPI"]
        )
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": "حدث خطأ أثناء استرجاع معلومات اللاعب."}), 404

if __name__ == '__main__':
    app.run(port=5000)
