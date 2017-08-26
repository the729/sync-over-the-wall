# Sync Over the Wall

Redirecting Resilio Sync's tracker and relay connection through a SOCKS server, without using global proxy settings.

通过SOCKS代理连接Resilio Sync的tracker和relay服务器，保持peer连接仍然直连。

# Background 背景

Resilio Sync's tracker and relay servers are block by The Wall. Without trackers, Sync can not discover peers on the Internet. 

Resilio Sync的服务器被和谐了，没有tracker服务器，就没有办法找到P2P的邻居节点。

Sync does provide a global proxy function, which will redirect both peer connections and server connections through the proxy. It will slow down peer connection speed and it's conflicting to the P2P nature of Sync. 

Sync软件可以设置全局代理，但这样和邻居的连接也经过代理，速度慢、流量大，而且和P2P的思想相违背。

# Before we start 在开始工作前

The tools are written in Python. Make sure you have the right environment to run these scripts.

这个工程是Python写的，因此你需要合适的Python 2.7运行环境来运行这些代码。

## For Mac Users 对于Mac用户

Download the source code. Install PySocks package (type the following command in a Terminal window):

Mac自带了Python环境，只需要安装PySocks库即可。在命令行用下面的指令安装：

```
pip install PySocks
```

## For Windows Users 对于Windows用户

I have created an executable package with py2exe. You can download it here: https://github.com/the729/sync-over-the-wall/raw/master/bin/sync-over-the-wall-x64bin.zip

我用py2exe创建了一个可以直接运行的exe文件，可以在上面那个链接中下载。

# How it works 如何工作的？

There are 2 ways to use sync-over-the-wall. You should choose one.

共有两种方式来使用这个工具，而且你得选择一种。

For Method 1, you need a SOCKS4/SOCKS5 proxy server that can go through The Wall. The downside of this method is that you have to keep a script running on your computer all the time when you use Sync.

第一种方法，需要一个可以翻墙的SOCKS4/5代理服务器即可。用这个方法，你需要在使用Sync的时候，一直保持一个后台脚本的运行。

For Method 2, you need a server that can go through The Wall, and you can configure iptables port forwarding on it. Normally, you can use a cloud VPS such as AWS. This way, you don't have to keep any script running while you use Sync.

第二种方法，需要一个可以翻墙的服务器，而且你可以在服务器上配置iptables转发规则。你可以用诸如AWS或者阿里云香港的云服务器。这样就不需要在使用中在后台跑任何脚本了。

Method 2 is recommended if you have the resources.

如果有能力搞定云服务器，推荐使用方法2。

Following are the detailed explaination and instructions. The original Sync system works like this:

接着看下面的具体原理和配置方法。下图是Sync本身的链接关系图。

![Original-System](https://github.com/the729/sync-over-the-wall/raw/master/doc/original.png "Original system")

## Method 1 方法一

![Method1](https://github.com/the729/sync-over-the-wall/raw/master/doc/method1.png "Use a SOCKS proxy to access tracker")

### Let Sync cache sync.conf 让Sync下载并缓存我们的sync.conf

First, rename sync.method1.conf to sync.conf. Normally, you don't have to edit it. 

首先，把sync.method1.conf文件重命名为sync.conf。这个文件通常不再需要修改了。

Run config\_server.py (or config\_server.exe) with Admin previledge. It uses hosts file to redirect Sync software to our fake config server. That's why we need Admin.

以管理员权限运行config\_server.py（或exe）。之所以需要管理员权限，是因为我们要修改hosts文件。

On Windows, right-click config\_server.exe and choose "Run as Administrator". 

用Windows，可以右键点击config\_server.exe，选择“以管理员运行”。

On Mac, from a terminal, type the command:

用Mac，在终端窗口敲下面的指令即可。

```
sudo python config_server.py
```

After the fake server is properly running, you have to restart Sync software according to the prompt. 

当我们冒充的config服务器启动后，你需要根据窗口中的提示，重启Sync。

After Sync has downloaded the config file, the fake server will shutdown automatically, and the hosts file will be restored. Since the real config.resilio.com is blocked, Sync can not download the real tracker list. So it will keep using our fake version, which is cached.

重启Sync后，它会从我们的冒充服务器下载sync.conf文件，并保存在缓存中。此后，我们的冒充服务器就会自动关闭，然后自动恢复hosts文件的设置。因为真的config.resilio.com被和谐了，所以此后Sync无法获得真的sync.conf文件，就会一直使用缓存中的数据。

If the program blocks and does not finish after Sync is restarted, it is probably because the automated script does not set your hosts file properly. You can do it manually. Add the following entry in your hosts file.

如果重启了Sync之后，程序卡住了而没有自动执行完成，那多半是因为它没能正确设置hosts文件。你可以尝试在hosts文件中手动加入下面的条目。

```
127.0.0.1    config.resilio.com
```

### Start tracker proxy 启动本机转发服务

Rename proxy.method1.conf to proxy.conf, and edit it with your own SOCKS4/5 proxy server address and port. Be careful that this file must be a valid JSON.

把proxy.method1.conf重命名为proxy.conf，并修改这个文件，写入你的SOCKS4/5服务器的地址和端口。注意这个文件是JSON格式的。

Run tracker\_proxy.py (or tracker\_proxy.exe). It does not need special previledge. It will transparently redirect Sync tracker connection to the SOCKS server configured in proxy.conf. This script should be kept running.

启动tracker\_proxy.py（或exe），它不需要管理员权限。它会利用刚刚在proxy.conf中定义的SOCKS代理，在本机建立透明的TCP转发服务。这个脚本需要一直在后台运行。

## Method 2 方法二

![Method2](https://github.com/the729/sync-over-the-wall/raw/master/doc/method2.png "Using a TCP forwarding server to access trackers")

### Let Sync cache sync.conf 让Sync下载并缓存我们的sync.conf

This step is very similar to the same step in Method 1. Rename sync.method2.conf to sync.conf, and edit it to point it directly towards your port-forwarding server.

第一步和方法一的第一步非常相似。同样需要重命名sync.method2.conf，注意这时需要修改这个文件，写入你的服务器的地址和端口。

Then, follow the same steps as Method 1 to let Sync cache the tracker list.

接着按照方法一中这一步骤的方法，让Sync从冒充服务器上获取并缓存sync.conf文件。

### Config your port-forwarding server 配置你的TCP转发服务器

Assuming your server's public IP address is 111.111.111.111, and 173.244.217.42 and 107.182.230.198 are Sync's primary tracker and relay server:

假设你的服务器IP地址是111.111.111.111。Sync的真是Tracker和Relay服务器地址是173.244.217.42和107.182.230.198。在服务器上用下面指令配置TCP端口转发。

```
iptables -t nat -A PREROUTING -p tcp -m tcp --dport 4000 -j DNAT --to-destination 173.244.217.42:4000

iptables -t nat -A POSTROUTING -d 173.244.217.42 -p tcp -m tcp --dport 4000 -j SNAT --to-source 111.111.111.111

iptables -t nat -A PREROUTING -p tcp -m tcp --dport 3000 -j DNAT --to-destination 107.182.230.198:3000

iptables -t nat -A POSTROUTING -d 107.182.230.198 -p tcp -m tcp --dport 3000 -j SNAT --to-source 111.111.111.111
```

# Credits 鸣谢和代码引用

TCP tee proxy code is based on https://gist.github.com/jwustrack/0c7cb063a28ce14766d421e8d8a12fcc

TCP三通代理代码是基于上面链接中的gist.
