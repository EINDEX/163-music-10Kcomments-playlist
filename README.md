# 163-music-comments-playlist
网易云音乐 评论过万歌曲 自动生成歌单

感谢 [MusicBox](https://github.com/darknessomi/musicbox) 提供的登录解决方案

运行需要：
- pymongo: mongodb 作为数据存储
- requests: 网络请求
- Crypto: 密码库

使用前先配置:
- 账号
```python
text = {
    'username': '账号',
    'password': '密码',
    'rememberLogin': 'true'
}
```

待添加功能：
- 自动生成歌单
