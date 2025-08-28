import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

// 配置axios基础URL，指向你的Flask后端
const API_BASE = 'http://localhost:5000/api';

function App() {
  const [posts, setPosts] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  // 加载文章列表
  const fetchPosts = async () => {
    try {
      const response = await axios.get(`${API_BASE}/posts`);
      setPosts(response.data);
    } catch (error) {
      console.error("Failed to fetch posts:", error);
    }
  };

  // 创建新文章
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !content) return;

    try {
      await axios.post(`${API_BASE}/posts`, { title, content });
      setTitle(''); // 清空表单
      setContent('');
      fetchPosts(); // 重新加载列表
      alert('文章发布成功！');
    } catch (error) {
      console.error("Failed to create post:", error);
      alert('发布失败，请检查控制台日志。');
    }
  };

  // 组件挂载时加载文章
  useEffect(() => {
    fetchPosts();
  }, []);

  return (
    <div className="app" style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>我的个人博客 (Windows版)</h1>

      {/* 创建文章的表单 */}
      <form onSubmit={handleSubmit} style={{ marginBottom: '2rem', padding: '1rem', border: '1px solid #ccc' }}>
        <h2>撰写新文章</h2>
        <div style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            placeholder="输入文章标题..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box' }}
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <textarea
            placeholder="输入文章内容..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows="5"
            style={{ width: '100%', padding: '0.5rem', boxSizing: 'border-box' }}
          />
        </div>
        <button type="submit" style={{ padding: '0.5rem 1.5rem' }}>发布文章</button>
      </form>

      <hr />

      {/* 文章列表 */}
      <h2>文章列表</h2>
      {posts.length === 0 ? (
        <p>还没有文章，赶快写一篇吧！</p>
      ) : (
        <div>
          {posts.map(post => (
            <article key={post.id} style={{ border: '1px solid #eee', padding: '1rem', marginBottom: '1rem' }}>
              <h3>{post.title}</h3>
              <p><small>发布时间: {new Date(post.created_at).toLocaleString('zh-CN')}</small></p>
              <p style={{ whiteSpace: 'pre-wrap' }}>{post.content}</p>
            </article>
          ))}
        </div>
      )}
    </div>
  )
}

export default App