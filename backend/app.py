import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # 处理跨域请求
import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


# 从环境变量读取配置，设置默认值用于开发环境
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database_url = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

# 初始化扩展
db = SQLAlchemy(app)

# 配置CORS - 允许前端域访问
frontend_url = os.environ.get('FRONTEND_URL', 'https://myblog-beta-five.vercel.app')
CORS(app, origins=[frontend_url, "http://localhost:5173"])


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
    logger.info("数据库初始化完成")

# ！！！确保CORS配置也应用到OPTIONS方法的预检请求上
# 例如，为你的路由添加对OPTIONS方法的支持
@app.route('/api/posts', methods=['GET', 'POST', 'OPTIONS'])  # 添加OPTIONS
def handle_posts():
    # 这个函数现在会处理预检请求
    if request.method == 'OPTIONS':
        # 对于OPTIONS请求，直接返回200，CORS中间件会处理头部
        return '', 200

# 同样为带参数的路由添加OPTIONS
@app.route('/api/posts/<int:post_id>', methods=['GET', 'DELETE', 'OPTIONS'])
def handle_post(post_id):
    if request.method == 'OPTIONS':
        return '', 200

# 添加根路由 - 这是解决404问题的关键
@app.route('/')
def index():
    return jsonify({
        "message": "博客API服务运行正常",
        "endpoints": {
            "获取所有文章": "GET /api/posts",
            "获取单篇文章": "GET /api/posts/<id>",
            "创建新文章": "POST /api/posts",
            "删除文章": "DELETE /api/posts/<id>"
        }
    })


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


# 健康检查端点 - Railway等平台可能需要这个
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.utcnow().isoformat()})


if __name__ == '__main__':
    # 从环境变量获取端口，默认为5000
    port = int(os.environ.get('PORT', 5000))
    # 生产环境关闭调试模式
    debug = os.environ.get('FLASK_ENV') == 'development'

    logger.info(f"启动服务器，端口: {port}, 调试模式: {debug}")
    app.run(debug=debug, host='0.0.0.0', port=port)