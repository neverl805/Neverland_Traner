# Neverland_Trainer

#### 介绍
半自动模型识别标注

结合了各大现有模型进行辅助打标，提高打标效率
由于借助了多个深度学习模型 代码整体偏重，可自行做调整二开


目前正在开发重构中，欢迎各位大佬指点
wx: xu970821582 我是小菜鸡 人够可考虑拉群交流 方向 (偏web3 ai)

#### 安装教程
##### cpu 安装
1. pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
2. pip install paddleocr -i https://pypi.tuna.tsinghua.edu.cn/simple
3. pip install torch torchvision -i https://pypi.tuna.tsinghua.edu.cn/simple
##### gpu安装
1. python -m pip install paddlepaddle-gpu==2.6.0.post120 -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html
2. pip install paddleocr
3. pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

###### PyQt5安装轻量版
pip install PyQt-Fluent-Widgets -i https://pypi.org/simple/

##### 其他包
pip install loguru -i https://pypi.tuna.tsinghua.edu.cn/simple

pip install ddddocr -i https://pypi.tuna.tsinghua.edu.cn/simple

pip install ruamel.yaml -i https://pypi.tuna.tsinghua.edu.cn/simple

pip install open_clip_torch -i https://pypi.tuna.tsinghua.edu.cn/simple
##### 特别说明
paddlepaddle跟clip只能一个gpu一个cpu
#### 使用说明
欢迎在源码上二开 或者有什么更好的思路结合现代模型来辅助打标可以交流一下

1.  python main.py


快捷键:

w 绘制矩形
a 上一张 
d 下一张
s 保存
delete 删除

孪生打标:
a 不同类型
d 相同类型

clip的用法需要先加载标签txt，再加载模型去识别

目标检测 分类方面,个人建议先大致练一个yolo模型，然后导入模型辅助继续打标提高效率


#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request

