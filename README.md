# 163-music-comments-playlist
网易云音乐 评论过万歌曲 自动生成歌单

感谢 [MusicBox](https://github.com/darknessomi/musicbox) 提供的登录解决方案

每次通过API 获取100首歌曲的信息(会将读取id暂存到 `playid.info` 中,可用redis等服务实现分布式),将歌曲信息输入队列后交由给获取线程执行取歌。

运行需要：
- PyMySQL: MySQL 作为数据存储
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
- 数据库
```python
def get_db_conn():
    return pymysql.connect(host='host',
                           port=3306,
                           user='user',
                           password='pwd',
                           charset='utf8',
                           db='db',
                           cursorclass=pymysql.cursors.DictCursor)
```

待添加功能：
- 自动生成歌单
