# AGV-cube
使得树莓派驱动的小车根据所面对的正方体颜色行走的程序。只需要使用摄像头作为输入，不需要超声测距和电机编码器输入。  
Allow AGV powered by RPi to run and turn according to front surface of cubes. Input only includes camera, does not require ultrasound or encoder.

## GPL-3.0 协议 LICENSE
如果您修改了代码，按规定也必须开源。但是我没有办法监督和强制您做这件事情，请视其为君子协定。只修改参数则并不需要开源。  
Any code edition is expected to be open-sourced as well, but I cannot force you to do it. Be wise to do so.

## 运行前的准备 Preparation

您需要 opencv，即能`import cv2`。这理论上也可以通过 pip 安装，但鉴于树莓派的羸弱性能，建议您使用 apt-get 直接安装二进制的编译成品。  
Requires opencv as well, I recommend installing binaries with apt-get for the poor performance of RPi. Installing with pip is possible but not recommended.
```bash
sudo apt-get install python-opencv
```

## 代码逻辑 Logic

### 如果检测到符合条件的图形（要求为：通过饱和度阈值处理后的图像中的封闭图形，面积在一定范围内）则：  
  If found eligible shape (with Saturation threshold, and size in certain range):  
  记录其重心横坐标 cX。Save current center X as cX.
  #### 如果在图像边缘（cX距离视野两侧较近，魔方即将离开视野，这时候应该离得比较近了）
  If near edges of vision:  
  直行 Go straight
  #### 否则 Otherwise（魔方在视野比较中间的位置）
  根据面积和 cX 以及颜色计算出目标位置 Calculate target x with cX, color and size.
### 否则 Otherwise
  #### 如上次记录的 cX 小于一半视野宽度（即魔方是从视野左侧离开的）
  If last recorded cX is less than half of vision width:  
  左转 Turn Left
  #### 否则 Otherwise
  右转 Turn Right

## 可能需要在调试中修改的量为：
- 颜色（可能的返回值为 red orange green blue yellow）此代码为绿色从右过，请根据自己的需求修改   
- 颜色色相对应的角度（HSV 空间内 H 的范围），请参考 Hue  
- GPIO 端口  
- PID 系数  
- 电机基础速度和转向控制量（有些小车重心比较靠后，如果启动时电机给的比较大会抬头，为了防止抬头，设计了缓起，故这里每种都需要需要两套参数，即起步阶段和正常运行阶段）  
- 缓起切换到正常速度所需要的循环数（例如，若您的车重心已经很靠前即不会抬头，那么可以将循环数设置为0，直接进入正常速度）
- 目标位置限制（即防止计算出的转向量过大）  
- 边缘判定阈值（即离视野边缘多近时，认为到魔方旁边了，直行）  
- 与正方体目标距离系数


## 调试助手
在正常运行代码后会生成一个 movie.avi 文件用于诊断故障。  

另外您可以使用 assist.py 辅助调试，其会显示当前的图像识别结果与预计的调节量（实际上就是实时显示的 movie.avi，但不会启动电机）。按 q 退出。

## 操作提示
运行代码后，在初始化结束后会输出 Ready，此时按回车启动电机进入主循环。  
在主循环按 Ctrl+C 触发 KeyboardInterrupt 结束程序，同时进行视频文件的保存，之后程序会自动退出。

## 注意
该代码运行成功与否，极度依赖于初始摆放位置和角度，请自行摸索如何摆放。若能通过第一个正方体，则后续两个正方体通过的概率为 80% 以上。  
我可能会在有反馈意见后更新代码，你可以定期来查看是否有更新。  
请同时将这里的所有Python文件放在同目录下。
