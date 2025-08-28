from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # 处理跨域请求
import datetime

app = Flask(__name__)
# 配置数据库URI，使用SQLite，数据库文件为blog.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db = SQLAlchemy(app)
CORS(app)  # 允许所有域访问API，方便开发

# 定义数据模型（数据库表）
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        """将模型实例转换为字典，方便json化"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }

# 创建数据库表（如果不存在）
with app.app_context():
    db.create_all()

# 定义API路由
# 1. 获取所有文章列表
@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify([post.to_dict() for post in posts])

# 2. 获取单篇文章
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())

# 3. 创建新文章
@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    if not data or not 'title' in data or not 'content' in data:
        return jsonify({"error": "Missing title or content"}), 400

    new_post = Post(title=data['title'], content=data['content'])
    db.session.add(new_post)
    db.session.commit()
    return jsonify(new_post.to_dict()), 201  # 201 Created

# 4. (可选) 删除文章
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return '', 204  # 204 No Content

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # 在5000端口运行，开启调试模式