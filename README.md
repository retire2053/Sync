# Sync
  
## 起源
虽然说云存储已经很方便了，但是我还是会有一些文档想要在我的多个硬盘中进行备份，所以需要一个sync的能力。  
之前使用windows上的SyncToy，不过随着个人使用平台迁移到Mac和Linux，就没有找到很好的免费工具。  
其实所需的功能也很简单，就是要能够查询、检索和备份。  
  
## 使用办法
python3 Sync.py <in_dir> <out_dir> <persistent_file>
1.<in_dir>要同步哪个目录，就输入目录的位置
2.<out_dir>要同步到哪个目录下，就输入目录的位置
3.<persistent_file> 这个配置要存储在哪里