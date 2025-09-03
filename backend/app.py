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


# 添加根路由
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


# 健康检查端点
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.datetime.utcnow().isoformat()})


# 定义API路由 - 确保每个路由都包含OPTIONS方法
@app.route('/api/posts', methods=['GET', 'POST', 'OPTIONS'])
def handle_posts():
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers.add('Access-Control-Allow-Origin', frontend_url)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response

    # 处理GET请求 - 获取所有文章
    if request.method == 'GET':
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return jsonify([post.to_dict() for post in posts])

    # 处理POST请求 - 创建新文章
    if request.method == 'POST':
        data = request.get_json()
        if not data or not 'title' in data or not 'content' in data:
            return jsonify({"error": "Missing title or content"}), 400

        new_post = Post(title=data['title'], content=data['content'])
        db.session.add(new_post)
        db.session.commit()
        return jsonify(new_post.to_dict()), 201  # 201 Created


@app.route('/api/posts/<int:post_id>', methods=['GET', 'DELETE', 'OPTIONS'])
def handle_post(post_id):
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers.add('Access-Control-Allow-Origin', frontend_url)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, DELETE, OPTIONS')
        return response

    # 处理GET请求 - 获取单篇文章
    if request.method == 'GET':
        post = Post.query.get_or_404(post_id)
        return jsonify(post.to_dict())

    # 处理DELETE请求 - 删除文章
    if request.method == 'DELETE':
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return '', 204  # 204 No Content


if __name__ == '__main__':
    # 从环境变量获取端口，默认为5000
    port = int(os.environ.get('PORT', 5000))
    # 生产环境关闭调试模式
    debug = os.environ.get('FLASK_ENV') == 'development'

    logger.info(f"启动服务器，端口: {port}, 调试模式: {debug}")
    app.run(debug=debug, host='0.0.0.0', port=port)