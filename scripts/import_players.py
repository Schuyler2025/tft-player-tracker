"""
批量导入选手脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tracker import PlayerTracker
from utils.helpers import setup_logger


def import_players_from_file(file_path: str):
    """从文件导入选手列表"""
    setup_logger()
    tracker = PlayerTracker()
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    success_count = 0
    fail_count = 0
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        try:
            # 格式: GameName#TagLine
            if '#' not in line:
                print(f"⚠️  格式错误，跳过: {line}")
                continue
            
            game_name, tag_line = line.split('#', 1)
            game_name = game_name.strip()
            tag_line = tag_line.strip()
            
            print(f"添加选手: {game_name}#{tag_line}...", end=' ')
            
            if tracker.add_player(game_name, tag_line):
                print("✅")
                success_count += 1
            else:
                print("❌")
                fail_count += 1
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            fail_count += 1
    
    print(f"\n导入完成: 成功 {success_count}, 失败 {fail_count}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python import_players.py <players_file>")
        print("示例: python import_players.py players.txt")
        sys.exit(1)
    
    import_players_from_file(sys.argv[1])
