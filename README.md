<div align="center">
  <h1 align="center"> quest teleop piper </h1>
  <h3 align="center"> Agilex Robotics </h3>
  <p align="center">
    <a href="README.md"> English </a> | <a>中文</a> 
  </p>
</div>




## 介绍

该仓库实现了使用 meta quest2/3 VR 套装对 piper 机械臂进行遥操作。

### 准备工作 

1、安装依赖

```bash
sudo apt install android-tools-adb

conda create -n vt python=3.9

conda activate vt

conda install pinocchio==3.2.0 casadi==3.6.7 -c conda-forge

pip install meshcat rospkg pyyaml pure-python-adb piper-sdk
```

2、配置您的 quest 设备

- quest必须支持开发者模式

  如在 quest 设备上找不到开发者模式，请参考该链接配置 quest 设备。

  点击：[oculus_reader](https://github.com/rail-berkeley/oculus_reader)

- 在quest上安装`alvr_client_android.apk`和`teleop-debug.apk`文件，文件在代码里面的`oculus_reader/APK`目录下。

  - [步骤1] 到meta商店安装Mobile VR Station 应用(联网)

  - [步骤2] 将 quest 与 pc 相连，开启 USB调试，在 pc 上显示新设备接入后，把要上述 apk 文件下载并复制到 quest的 Dowanload 目录里面
  
  - [步骤3] 开启Mobile VR Station => Configuration Wizard => Show All Options => Configuration Scoped Storage => Step1: Request Access => 选择根目录Dowanload 里面刚刚步骤2放的apk 点击类似放大的按钮会弹出一个窗口，在弹出的窗口里点击安装

- 如果上一步无法安装可以用如下链接中的方案，注意需要windows
  - <https://www.bilibili.com/opus/267781439861047911>
  - 其中的SideQuest app界面会更新，但是一定会有安装apk功能 <https://github.com/SideQuestVR/SideQuest/releases>

3、将代码克隆下来并编译：

```bash
git clone git@github.com:agilexrobotics/questVR_ws.git

cd questVR_ws 

catkin_make
```

我们在 Ubuntu 20.04 上测试了我们的代码，其他操作系统可能需要不同的配置。

有关更多信息，您可以参考 [開始使用 Meta Quest 2](https://www.meta.com/zh-tw/help/quest/articles/getting-started/getting-started-with-quest-2/?srsltid=AfmBOoqvDcwTtPt2P9o6y3qdXT_9zxz4m8yyej4uwLGEXVXv6KAr3QQz) 、[Piper_ros](https://github.com/agilexrobotics/Piper_ros)、[oculus_reader](https://github.com/rail-berkeley/oculus_reader)。

4、进入到 piper_description 功能包下，将 urdf 目录下的 piper_description.urdf 所有 STL 文件的用户名修改成你的用户名，例如：

```xml
<geometry>
        <mesh
          filename="/home/agilex/questVR_ws/src/Piper_ros/src/piper_description/meshes/base_link.STL" />
</geometry>

修改成

<geometry>
        <mesh
          filename="/home/<your name>/questVR_ws/src/Piper_ros/src/piper_description/meshes/base_link.STL" />
</geometry>
```

### 代码架构说明

oculus_reader，该存储库提供了从 Quest 设备读取位置和按下按钮的工具。

以VR眼镜作为基站，将手柄的与基站的TF关系传输给机械臂。

```bash
├── APK    #apk文件
│   ├── alvr_client_android.apk
│   └── teleop-debug.apk
├── CMakeLists.txt
├── config
│   └── oculus_reader.rviz
├── launch	#启动文件
│   ├── teleop_double_piper.launch
│   └── teleop_single_piper.launch
├── package.xml
└── scripts
    ├── buttons_parser.py
    ├── FPS_counter.py
    ├── install.py
    ├── oculus_reader.py
    ├── piper_control.py		#机械臂控制接口
    ├── teleop_double_piper.py	#遥操作双臂代码
    ├── teleop_single_piper.py	#遥操作单臂代码
    └── tools.py
```

## 软件启动

1、机械臂使能

**单piper使能**：

将机械臂的can线接入电脑

然后执行：

```bash
cd ~/questVR_ws/src/Piper_ros

bash can_activate.sh can0 1000000
```

**左右双piper使能**：


先将左机械臂的can线接入电脑

然后执行：

```bash
cd ~/questVR_ws/src/Piper_ros

bash find_all_can_port.sh 
```

终端会出现左机械臂的端口号，接着将右机械臂的can线接入电脑

再次执行：

```bash
bash find_all_can_port.sh 
```

终端会出现左机械臂的端口号。

将这左右两个端口号复制到 can_config.sh 文件的 111 和 112 行，如下所示：

```bash
# 预定义的 USB 端口、目标接口名称及其比特率（在多个 CAN 模块时使用）
if [ "$EXPECTED_CAN_COUNT" -ne 1 ]; then
    declare -A USB_PORTS 
    USB_PORTS["1-8.1:1.0"]="left_piper:1000000"  #左机械臂
    USB_PORTS["1-8.2:1.0"]="right_piper:1000000" #右机械臂
fi
```

保存完毕后，激活左右机械臂使能脚本：

```bash
cd ~/questVR_ws/src/Piper_ros

bash can_config.sh 
```


2、启动遥操机械臂

```bash
source /home/agilex/questVR_ws/devel/setup.bash

conda activate vt

roslaunch oculus_reader teleop_single_piper.launch    # 单臂遥操

or

roslaunch oculus_reader teleop_double_piper.launch    # 双臂遥操
```

在启动遥操代码时出现该错误时：

```bash
Device not found. Make sure that device is running and is connected over USB
Run `adb devices` to verify that the device is visible.
```

说明了VR头盔未开启调试模式，开启调试模式方法步骤如下：

1. 使用 USB-C 线将VR头盔连接到计算机，然后佩戴该设备。

2. 当在通知中出现“检测到USB”，点击一下该通知。

   ![img error](img/2.png)

3. 第一次开启程序，会出现上面的报错。

4. 当设备上出现提示时，接受**允许 USB 调试**和**始终允许从此计算机进行。**

   ![img error](img/1.png)

5. 关掉程序，再次运行。





## 操作说明

> 注意⚠️：
>
> - 请一定要确保VR屏幕保持常亮，否则TF会乱飘导致遥操作机械臂乱飞，我们建议在VR眼镜里面拿东西遮住感应器，使其保持常亮状态。
> - 开启程序后，请一定要确保手柄在VR视野里以及rviz里面的坐标稳定不会乱飘，然后按住按键“A”||“X”使机械臂复位，复位后才可进行遥操做，否则机械臂也会乱飞。
> - 在遥操 piper 启动后，请注意观察网页端的机械臂是否乱飘，

- 遥操单臂使用右手手柄，开始遥操前确保机械臂回到初始姿态，按住按键 “A” 能使机械臂回到初始位置，长按按键 “B” 为遥操机械臂，松开为停止控制。遥操双臂同理。  

- 为了操作的人身安全以及减少对机械臂的损害，在遥操结束后，请确保机械臂回到初始位置附件再按下“A”||“X”键复位。













