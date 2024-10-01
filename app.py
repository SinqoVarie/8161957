from flask import Flask

# إنشاء كائن التطبيق
app = Flask(__name__)

# تعريف المسار الرئيسي الذي يعرض "مرحبًا"
@app.route('/')
def hello():
    return 'مرحبًا'

# التأكد من تشغيل التطبيق عند استدعائه
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
