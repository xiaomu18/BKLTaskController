# BKLTaskController
基于 Python 的轻量级远程管理部署系统

# BKLTaskController V3 正在重写中...
特征
1. 启动脚本 HASH 校验
2. 重写 BKLSocketProtocol, 使用异步，杜绝粘包或者多个数据包发送时混乱
3. 可以获取服务端到实例的延迟
4. 重写通信协议，新增 Exchange 协议，使每个任务可以单独获取返回值
5. 可以使用构建的专属 python 环境，实例不需要安装 python 环境
6. 运行程序时支持向控制台输入字符
7. 优化 V3 代码结构
8. 添加更多 API 和功能选项，扩展性 ++
9. 现在可以与 BKLTaskDaemon 配合，防止意外退出
